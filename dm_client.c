
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/tcp.h>

//#include <errno.h>

#include "log.h"
#include "base64.h"
#include "dm_client.h"

int tcp_create(void)
{
	int fd = socket(AF_INET, SOCK_STREAM, 0) ;
	if(fd < 0 ) {
		perror("tcp socket create");
		return -1 ;
	}
	int no_nagle_flag = 1;
	if( setsockopt( fd, IPPROTO_TCP, TCP_NODELAY, (const void*)&no_nagle_flag, sizeof(int) ) ) {
		perror("tcp nagle flag set");
		return -1 ;
	}
	return fd;
}

int tcp_connect(int fd)
{
	if( fd <=0 ) {
		return -1 ;
	}

	struct sockaddr_in              client_addr;
	struct sockaddr_in              server_addr;

	client_addr.sin_family          = AF_INET ;
	client_addr.sin_addr.s_addr     = INADDR_ANY ;
	client_addr.sin_port            = 0 ;

	server_addr.sin_family          = AF_INET ;
	server_addr.sin_port            = htons(DM_SERVER_PORT);
	inet_aton(DM_SERVER_IP,         &server_addr.sin_addr);

	if( bind   (fd, (struct sockaddr *) &client_addr, sizeof(struct sockaddr) ) < 0 ) {
		perror("tcp socket bind");
		return -1 ;
	}

	if( connect(fd, (struct sockaddr *) &server_addr, sizeof(struct sockaddr) ) < 0 ) {
		perror("tcp socket connect");
		return -1 ;
	}

	DEBUGP4("connect server ip is %s, port is %d .\n", inet_ntoa(server_addr.sin_addr), ntohs(server_addr.sin_port));

	socklen_t addr_size = sizeof(struct sockaddr_in);
	if( getsockname(fd, (struct sockaddr *) &client_addr, &addr_size ) < 0 ) {
		perror("tcp socket getsockname") ;
		return -1 ;
	}

	DEBUGP4("tcp bind  port is %d .\n", ntohs(client_addr.sin_port));

	return fd;
}

void tcp_close(int fd)
{
	if (shutdown(fd, SHUT_RDWR) < 0 ) {
		perror("tcp_shutdown");
	}

	if (close(fd) < 0 ) {
		perror("tcp_close");
	}
}

//---------------------------------------------------------

int dm_send(int fd, PROTO_SEND* proto_send, int send_size)
{
	char* buff = (char *)proto_send;
	int   len  = send_size;

	int   ret  = send(fd, buff, len, 0);
	if(ret <= 0 ) {
		perror("tcp_send : send");
		return -1;
	}

	return len;
}

int dm_recv(int fd, PROTO_RECV* proto_recv, int recv_size)
{
	char* buff = (char *)proto_recv;
	int   len  = 0;

	int   ret  = 0;
	do {
		ret = recv(fd, &(buff[len]), recv_size - len, 0);
		if(ret < 0 ) {
			perror("tcp_recv : recv");
			return -1;
		}
		len += ret;
	}while(ret != 0 && len < recv_size);

	return len;
}

int dm_proto_make(PROTO_SEND* proto_send, int user_id, char* image, int imagelen)
{
	proto_send->nTotalLen	  	= imagelen + 6 ;
	//proto_send->nProtocolID	= DM_PROTO_ID + user_id ;
	proto_send->nProtocolID	  	= DM_PROTO_ID + 1;
	proto_send->nBodyLen	  	= imagelen ;
	memcpy(proto_send->arBody, 	image, imagelen);

	return 4 + 2 + 4 + imagelen ;
}

int dm_proto_parse(PROTO_RECV* proto_recv)
{
	DEBUGP2(FUNC_NAME_HEAD"proto_recv->nCodeNum = %d \n", __func__, proto_recv->nCodeNum);
	return proto_recv->nCodeNum;
}

//---------------------------------------------------------

int dm_connect(void)
{
	return tcp_connect(tcp_create());
}

int dm_64_to_bin(char* pic_64, char* pic_bin)
{
	return Base64Decode(pic_bin, pic_64, strnlen(pic_64, MAX_IMAGELEN));
}

unsigned int dm_getimage(int fd, int user_id, char* pic_bin, int len)
{
	if(len >= MAX_IMAGELEN) {
		return ~0;
	}

	char send_buff[sizeof(PROTO_SEND)+1] = {0};
	char recv_buff[sizeof(PROTO_RECV)+1] = {0};

	PROTO_SEND* proto_send = (PROTO_SEND*) send_buff;
	PROTO_RECV* proto_recv = (PROTO_RECV*) recv_buff;

	int send_size = dm_proto_make(proto_send, user_id, pic_bin, len);
	int recv_size = sizeof(PROTO_RECV);

	if(dm_send(fd, proto_send, send_size) <= 0 ) { 
		tcp_close(fd);
		return ~0;
	}

	if(dm_recv(fd, proto_recv, recv_size) <= 0 ) {
		tcp_close(fd);
		return ~0;
	}

	tcp_close(fd);

	return dm_proto_parse(proto_recv);
}


