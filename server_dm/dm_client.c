
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/tcp.h>

#include "dm_client.h"

#define SERVER_PORT	9999
#define SERVER_IP	"127.0.0.1"

void proto_make(PROTO_SEND* proto_send, unsigned short priority, unsigned short userid, unsigned char image[], unsigned int imagelen)
{
	if(proto_send == NULL || imagelen >= MAX_IMAGELEN)
		return ;

	proto_send->priority 	= priority;
	proto_send->userid	= userid;
	proto_send->imagelen 	= imagelen;
	memcpy(proto_send->image, image, imagelen);
}

void proto_print(PROTO_RECV* proto_recv)
{
	if(proto_recv == NULL)
		return;

	printf("proto_recv->number : %-6u \n", proto_recv->number);
}

int proto_init(PROTO_SEND* proto_send)
{
	if(proto_send == NULL)
		return -1 ;

	unsigned char  image[] 	= "1234567890" ;
	unsigned short imagelen	= 10 ;

	proto_make(proto_send, 0, 127, image, imagelen);

	return 2 + 2 + 4 + imagelen ;
}

int tcp_create(void)
{
	int fd = socket(AF_INET, SOCK_STREAM, 0) ;
	if(fd < 0 ) {
		perror("tcp socket create");
		return -1 ;
	}
	int no_nagle_flag = 1;
	if( setsockopt( fd, IPPROTO_TCP, 	TCP_NODELAY, 	(const void*)&no_nagle_flag, 	sizeof(int) ) ) {
		perror("tcp nagle flag set");
		return -1 ;
	}
	return fd;
}

int tcp_connect(int fd)
{
	struct sockaddr_in  		client_addr;
	struct sockaddr_in  		server_addr;

	client_addr.sin_family          = AF_INET ;
	client_addr.sin_addr.s_addr     = INADDR_ANY ;
	client_addr.sin_port            = 0 ;

	server_addr.sin_family 		= AF_INET ;
	server_addr.sin_port 		= htons(SERVER_PORT);
	inet_aton(SERVER_IP, 		&server_addr.sin_addr);

	if( bind   (fd, (struct sockaddr *) &client_addr, sizeof(struct sockaddr) ) < 0 ) {
		perror("tcp socket bind");
		return -1 ;
	}

	if( connect(fd, (struct sockaddr *) &server_addr, sizeof(struct sockaddr) ) < 0 ) {
		perror("tcp socket connect");
		return -1 ;
	}

	printf("connect server ip is %s, port is %d .\n", inet_ntoa(server_addr.sin_addr), ntohs(server_addr.sin_port));

	socklen_t addr_size = 0;
	if( getsockname(fd, (struct sockaddr *) &client_addr, &addr_size ) < 0 ) {
		perror("tcp socket getsockname") ;
		return -1 ;
	}

	printf("tcp bind  port is %d .\n", ntohs(client_addr.sin_port));

	return 0;
}

void tcp_send(int fd)
{
	unsigned char buff[MAX_IMAGELEN + 8] = {0};
	PROTO_SEND* proto_send = (PROTO_SEND*) buff;

	memset(proto_send, 0, sizeof(PROTO_SEND));
	int len = proto_init(proto_send);
	if(len <= 0 ) {
		printf("tcp_send : init");
		return ;
	}

	int ret = send(fd, buff, len, 0);

	if(ret <= 0 ) {
		perror("tcp_send : send");
		return ;
	}
}

void tcp_recv(int fd)
{
	unsigned char buff[MAX_IMAGELEN + 8] = {0};
	PROTO_RECV* proto_recv = (PROTO_RECV*) buff;

	memset(proto_recv, 0, sizeof(PROTO_RECV));

	int len = 0 , ret = 0;
	do {
		ret = recv(fd, &(buff[len]), sizeof(buff) - len, 0);
		if(ret < 0 ) {
			perror("tcp_recv : recv");
			return ;
		}
		len += ret;
	}while(ret != 0 && len < MAX_IMAGELEN + 8);

	proto_print(proto_recv);
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

int main(void)
{
	int fd = 0;

	fd = tcp_create();

	tcp_connect(fd);

	tcp_send(fd);

	tcp_recv(fd);

	tcp_close(fd);

	return 0;
}

