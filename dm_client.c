
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/tcp.h>

#include "log.h"
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
	inet_aton(DM_SERVER_IP,            &server_addr.sin_addr);

	if( bind   (fd, (struct sockaddr *) &client_addr, sizeof(struct sockaddr) ) < 0 ) {
		perror("tcp socket bind");
		return -1 ;
	}

	if( connect(fd, (struct sockaddr *) &server_addr, sizeof(struct sockaddr) ) < 0 ) {
		perror("tcp socket connect");
		return -1 ;
	}

	DEBUGP4("connect server ip is %s, port is %d .\n", inet_ntoa(server_addr.sin_addr), ntohs(server_addr.sin_port));

	socklen_t addr_size = 0;
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

int dm_send(int fd, PROTO_SEND* proto_send)
{
	char* buff = (char *)proto_send;
	int   len  = sizeof(PROTO_SEND);

	int   ret  = send(fd, buff, len, 0);
	if(ret <= 0 ) {
		perror("tcp_send : send");
		return -1;
	}

	return len;
}

int dm_recv(int fd, PROTO_RECV* proto_recv)
{
	char* buff = (char *)proto_recv;
	int   len  = 0;

	int   ret  = 0;
	do {
		ret = recv(fd, &(buff[len]), sizeof(PROTO_RECV) - len, 0);
		if(ret < 0 ) {
			perror("tcp_recv : recv");
			return -1;
		}
		len += ret;
	}while(ret != 0 && len < sizeof(PROTO_RECV));

	return len;
}

void dm_proto_make(PROTO_SEND* proto_send, unsigned short priority, unsigned short userid, char* image, unsigned int imagelen)
{
	proto_send->priority      = priority;
	proto_send->userid        = userid;
	proto_send->imagelen      = imagelen;
	memcpy(proto_send->image,   image, imagelen);
}

int dm_proto_parse(PROTO_RECV* proto_recv)
{
	return proto_recv->number;
}

//---------------------------------------------------------

int dm_connect(void)
{
	return tcp_connect(tcp_create());
}

int dm_64_to_bin(char* pic_64, char* pic_bin)
{
	int len = strnlen(pic_64, MAX_IMAGELEN);
	memcpy(pic_bin, pic_64, len);
	return len;
}

unsigned int dm_getimage(int fd, int priority, int userid, char* pic_bin, int len)
{
	if(len >= MAX_IMAGELEN) {
		return ~0;
	}

	unsigned char send_buff[sizeof(PROTO_SEND)+1] = {0};
	unsigned char recv_buff[sizeof(PROTO_RECV)+1] = {0};

	PROTO_SEND* proto_send = (PROTO_SEND*) send_buff;
	PROTO_RECV* proto_recv = (PROTO_RECV*) recv_buff;

	dm_proto_make(proto_send, (unsigned short)priority, (unsigned short)userid, pic_bin, len);

	if(dm_send(fd, proto_send) <= 0 ) { 
		tcp_close(fd);
		return ~0;
	}

	if(dm_recv(fd, proto_recv) <= 0 ) {
		tcp_close(fd);
		return ~0;
	}

	tcp_close(fd);

	return dm_proto_parse(proto_recv);
}


