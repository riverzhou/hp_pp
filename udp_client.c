
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/udp.h>

#include "user.h"
#include "log.h"
#include "myssl.h"
#include "myxml.h"
#include "server.h"
#include "udp_client.h"

//==============================================

int udp_create(void)
{
	int fd = socket(AF_INET, SOCK_DGRAM, 0) ;
	if(fd <= 0 ) {
		perror("udp socket create");
		return -1 ;
	}
	struct timeval timeout = {UDP_TIMEOUT,0};
	if( setsockopt( fd, SOL_SOCKET, SO_RCVTIMEO, (const void*)&timeout, sizeof(struct timeval) ) ) {
		perror("udp send timeout set");
		return -1;
	}

	struct sockaddr_in              client_addr;
	client_addr.sin_family          = AF_INET ;
	client_addr.sin_addr.s_addr     = INADDR_ANY ;
	client_addr.sin_port            = 0 ;

	if( bind(fd, (struct sockaddr *) &client_addr, sizeof(client_addr) ) < 0 ) {
		perror("udp socket bind") ;
		return -1 ;
	}

	socklen_t addr_size = sizeof(struct sockaddr_in);
	if( getsockname(fd, (struct sockaddr *) &client_addr, &addr_size ) < 0 ) {
		perror("udp socket getsockname") ;
		return -1 ;
	}
	DEBUGP2(FUNC_NAME_HEAD"udp bind port is %d .\n", __func__, ntohs(client_addr.sin_port));

	return fd ;
}

int udp_send(int user_id, char* buff, int send_size)
{
	int group    	= pp_user[user_id].group;
	int fd 		= pp_user[user_id].session_udp.fd;
	int server_id	= 0;

	if(buff == NULL || fd <= 0){
		return -1;
	}

	if(send_size <= 0) {
		return 0;
	}

	if(group == 0)
		server_id = UDP_A;
	else
		server_id = UDP_B;

	int ret = sendto(fd, buff, send_size, 0,(struct sockaddr *)&(server[server_id].addr), sizeof(struct sockaddr_in));
	if(ret <= 0 ) {
		perror("udp_send : sendto");
		return -1;
	}
	DEBUGP2(FUNC_NAME_HEAD"udp sent %d : %d .\n", __func__, send_size, ret);

	return ret;
}

int udp_recv(int user_id, char* buff, int buff_size)
{
	int group    	= pp_user[user_id].group;
	int fd 		= pp_user[user_id].session_udp.fd;
	int server_id	= 0;

	pp_user[user_id].session_udp.flag_nodata  = 1;
	pp_user[user_id].session_udp.flag_timeout = 1;

	if(buff == NULL || fd <= 0){
		return -1;
	}

	if(group == 0)
		server_id = UDP_A;
	else
		server_id = UDP_B;

	struct sockaddr_in     		server_addr;
	memset(&server_addr,            0, sizeof(struct sockaddr_in));
	server_addr.sin_family          = AF_INET ;

	socklen_t addr_size = sizeof(struct sockaddr_in);
	int ret = recvfrom(fd, buff, buff_size, 0, (struct sockaddr *)&server_addr, &addr_size);
	if(ret <= 0 ) {
		if( errno == EAGAIN || errno == EWOULDBLOCK ) {
			return -1;
		}
		pp_user[user_id].session_udp.flag_timeout = 0;
		perror("udp_recv : recvfrom");
		return -1;
	}
	pp_user[user_id].session_udp.flag_timeout = 0;
	DEBUGP2(FUNC_NAME_HEAD"udp recv %d .\n", __func__, ret);

	if(server_addr.sin_addr.s_addr != server[server_id].addr.sin_addr.s_addr || server_addr.sin_port != server[server_id].addr.sin_port) {
		DEBUGP2(FUNC_NAME_HEAD"udp recv data is not from udp server \n", __func__);
		DEBUGP2(FUNC_NAME_HEAD"%u : %u, %u : %u \n", __func__, server_addr.sin_addr.s_addr, server[server_id].addr.sin_addr.s_addr, server_addr.sin_port, server[server_id].addr.sin_port);
		return -1;
	}
	pp_user[user_id].session_udp.flag_nodata  = 0;

	return ret;
}

void udp_close(int user_id)
{
	if( pp_user[user_id].session_udp.fd <= 0 )
		return;

	if( close(pp_user[user_id].session_udp.fd) < 0 ) {
		perror("udp_close");
	}

	pp_user[user_id].session_udp.fd = -1;
}

//---------------------------------------------------------------

int udp_data_encode(char* buff, int len)
{
	int  len1 = len >> 2;
	int  len2 = len &  3;
	int  *p1  = (int*) buff;
	char *p2  = &(buff[len1*4]);

	for(int i = 0; i < len1 ; i++) {
		p1[i] = ~p1[i];
	}
	for(int n = 0; n < len2 ; n++) {
		p2[n] = ~p2[n];
	}

	return len;
}

int udp_data_decode(char* buff, int len)
{
	int  len1 = len >> 2;
	int  len2 = len &  3;
	int  *p1  = (int*) buff;
	char *p2  = &(buff[len1*4]);

	for(int i = 0; i < len1 ; i++) {
		p1[i] = ~p1[i];
	}
	for(int n = 0; n < len2 ; n++) {
		p2[n] = ~p2[n];
	}

	return len;
}

//---------------------------------------------------------------

#define UDP_FORMAT	"<TYPE>FORMAT</TYPE><BIDNO>%.8d</BIDNO><VCODE>%s</VCODE>"
#define UDP_LOGOFF	"<TYPE>LOGOFF</TYPE><BIDNO>%.8d</BIDNO><VCODE>%s</VCODE>"

#define UDP_CLIENT	"<TYPE>CLIENT</TYPE><BIDNO>%.8d</BIDNO><VCODE>%s</VCODE>"

int udp_proto_format(int user_id, char* buff, int buff_len)
{
	char vcode_seed[40] = {0};	// 18 + 8
	char vcode[40]	    = {0};	// 32

	snprintf(vcode_seed, sizeof(vcode_seed)-1, "%s%.8d", pp_user[user_id].session_login.result_login.pid, pp_user[user_id].bidnumber);

	get_md5string_up(vcode, vcode_seed);

	snprintf(buff, buff_len, UDP_FORMAT, pp_user[user_id].bidnumber, vcode);

	return strnlen(buff, buff_len - 1);;
}

int udp_proto_logoff(int user_id, char* buff, int buff_len)
{
	char vcode_seed[40] = {0};	// 18 + 8
	char vcode[40]	    = {0};	// 32

	snprintf(vcode_seed, sizeof(vcode_seed)-1, "%s%.8d", pp_user[user_id].session_login.result_login.pid, pp_user[user_id].bidnumber);

	get_md5string_up(vcode, vcode_seed);

	snprintf(buff, buff_len, UDP_LOGOFF, pp_user[user_id].bidnumber, vcode);

	return strnlen(buff, buff_len - 1);;
}

int udp_proto_client(int user_id, char* buff, int buff_len)
{
	int len = 0;

	return len;
}

int udp_proto_parse(int user_id, char* buff, int len)
{
	int number = 0;
	XML_DICT xml_dict[MAX_XML_DICTLEN];
	memset(xml_dict, 0, sizeof(xml_dict));
	RESULT_UDP* result_udp = &pp_user[user_id].session_udp.result_udp;

	DEBUGP2(FUNC_NAME_HEAD"%s\n", __func__,  buff);
	myxml_parseMemory(buff, xml_dict, &number, MAX_XML_DICTLEN - 1);
	for(int i = 0 ; i < number ; i++ ){
		DEBUGP2(FUNC_NAME_HEAD"%32s = %s\n", __func__,  xml_dict[i].key, xml_dict[i].val);

		if(strcmp(xml_dict[i].key, "TYPE") == 0) {
			strncpy(result_udp->type, xml_dict[i].val, sizeof(result_udp->type) - 1);
			continue;
		}

	}

	return 0;
}

//---------------------------------------------------------------

int udp_login(int user_id)
{
	int fd = udp_create();
	if(fd <= 0 ) {
		return -1;
	}

	pp_user[user_id].session_udp.fd = fd;

	char buff[MAX_UDP_BUFFLEN] = {0};

	int len = udp_proto_format(user_id, buff, sizeof(buff));

	DEBUGP2(FUNC_NAME_HEAD"%s\n", __func__, buff);

	udp_data_encode(buff, len);

	int ret = udp_send(user_id, buff, len);

	return ret;
}

int udp_logout(int user_id)
{
	char buff[MAX_UDP_BUFFLEN] = {0};

	int len = udp_proto_logoff(user_id, buff, sizeof(buff));

	DEBUGP2(FUNC_NAME_HEAD"%s\n", __func__, buff);

	udp_data_encode(buff, len);

	int ret = udp_send(user_id, buff, len);

	udp_close(user_id);

	return ret;
}

int udp_getinfo(int user_id)
{
	char buff[MAX_UDP_BUFFLEN] 				= {0};
	char xml_buff[sizeof(buff) + sizeof("<XML></XML>")] 	= {0};

	int len = udp_recv(user_id, buff, sizeof(buff)); 
	if(len <= 0 ) {
		return -1;
	}

	udp_data_decode(buff, len);

	DEBUGP2(FUNC_NAME_HEAD"%s\n", __func__, buff);

	snprintf(xml_buff, sizeof(xml_buff)-1, "<XML>%s</XML>", buff);		// 收到的UDP包不是标准XML格式，需要加上XML的头

	int info = udp_proto_parse(user_id, xml_buff, len+sizeof("<XML></XML>"));

	return info;
}

//---------------------------------------------------------------
