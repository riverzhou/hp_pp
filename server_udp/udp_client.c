
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/udp.h>

#include "udp_client.h"

#define SERVER_PORT	999
#define SERVER_IP	"127.0.0.1"

#define MAX_BUFFLEN	8192 


void proto_udp_encode(char* buff, int len)
{
	for(int i = 0; i < len && buff[i] != 0; i++) {
		buff[i] = ~buff[i];
	}
}

void proto_udp_decode(char* buff, int len)
{
	for(int i = 0; i < len && buff[i] != 0; i++) {
		buff[i] = ~buff[i];
	}
}

void proto_print(char* buff)
{
	if(buff == NULL)
		return;

	proto_udp_decode(buff, MAX_BUFFLEN);

	buff[MAX_BUFFLEN-1] = 0;

	printf("buff : \n%s\n", buff);
}

int proto_init(char* buff, int len)
{
	if(buff == NULL)
		return -1 ;

	int buff_len = strnlen(LOGIN_STRING, len);;

	snprintf(buff, len, "%s", LOGIN_STRING);

	proto_udp_encode(buff, len);

	return buff_len ;
}

int udp_create(void)
{
	int fd = socket(AF_INET, SOCK_DGRAM, 0) ;
	if(fd < 0 ) {
		perror("udp socket create");
		return -1 ;
	}
	struct timeval timeout = {5,0};	
	if( setsockopt( fd, SOL_SOCKET, SO_RCVTIMEO, (const void*)&timeout, sizeof(struct timeval) ) ) {
		perror("udp send timeout set");
		return -1;
	}
	return fd;
}

int udp_connect(int fd)
{
	struct sockaddr_in  		client_addr; 	
	struct sockaddr_in      	server_addr;

	client_addr.sin_family 		= AF_INET ;
	client_addr.sin_addr.s_addr 	= INADDR_ANY ;
	client_addr.sin_port 		= 0 ;

	server_addr.sin_family          = AF_INET ;
	server_addr.sin_port            = htons(SERVER_PORT);
	inet_aton(SERVER_IP,            &server_addr.sin_addr);

	if( bind(fd, (struct sockaddr *) &client_addr, sizeof(client_addr) ) < 0 ) {
		perror("udp socket bind") ;
		return -1 ;
	}

	if( connect(fd, (struct sockaddr *) &server_addr, sizeof(struct sockaddr) ) < 0 ) {
		perror("udp socket connect");
		return -1 ;
	}

	printf("connect server ip is %s, port is %d .\n", inet_ntoa(server_addr.sin_addr), ntohs(server_addr.sin_port));

	socklen_t addr_size = 0;
	if( getsockname(fd, (struct sockaddr *) &client_addr, &addr_size ) < 0 ) {
		perror("udp socket getsockname") ;
		return -1 ;
	}

	printf("udp bind  port is %d .\n", ntohs(client_addr.sin_port));

	return 	0 ;
}

void udp_send(int fd)
{
	char buff[MAX_BUFFLEN] = {0};

	int len = proto_init(buff, MAX_BUFFLEN);
	if(len <= 0 ) {
		printf("udp_send : init");
		return ;
	}

	int ret = send(fd, buff, len, 0);

	if(ret < 0 ) {
		perror("udp_send : send");
		return ;
	}
}

void udp_recv(int fd)
{
	struct sockaddr_in  		server_addr; 	
	memset(&server_addr, 		0, sizeof(struct sockaddr_in));
	server_addr.sin_family 		= AF_INET ;

	char buff[MAX_BUFFLEN] = {0};

	int ret = recv(fd, buff, sizeof(buff), 0);
	if(ret < 0 ) {
		perror("udp_recv : recv");
		return ;
	}

	proto_print(buff);
}

void udp_close(int fd)
{
	if (close(fd) < 0 ) {
		perror("udp_close");
	}
}

int main(void)
{
	int fd = 0;

	fd = udp_create();

	udp_connect(fd);

	udp_send(fd);

	udp_recv(fd);

	udp_close(fd);

	return 0;
}

