
#include <pthread.h>

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "log.h"  
#include "myssl.h"  
#include "myudp.h"  
#include "proto_checkcode.h"  
#include "proto_make.h"  
#include "proto_parse.h"
#include "server.h"
#include "proc.h"
#include "myevent.h"
#include "myrand.h"

// DEBUGP2
// LOGP4

#define SEND_BUFF_SIZE 	4096
#define RECV_BUFF_SIZE  8192

//================================================================
//----------------------------------------------------------------

int proc_login(int user_id, int delay)
{
	int             group 		= pp_user[user_id].group;
	unsigned int    bidnumber 	= pp_user[user_id].bidnumber;
	unsigned int    bidpassword 	= pp_user[user_id].bidpassword;
	unsigned int    imagenumber 	= pp_user[user_id].session_login.image;
	char*           machinecode 	= pp_user[user_id].machinecode;
	RESULT_LOGIN*   result_login 	= &pp_user[user_id].session_login.result_login;

	int channel_id 			=-1 ;
	int server			=-1 ;	
	char proto[SEND_BUFF_SIZE] 	={0};
	char buff[RECV_BUFF_SIZE]  	={0};

	if(group == 0)
		server = LOGIN_A;
	else
		server = LOGIN_B;

	memset(proto, 0, sizeof(proto));
	proto_makelogin(
			group,
			bidnumber,
			bidpassword,
			imagenumber,
			machinecode,
			proto);

	channel_id = channel_findfree();

	if(pp_user[user_id].session_login.event_login_req != NULL){
		DEBUGT2("wait for conn to LOGIN server... \n");
		LOGT4("wait for conn to LOGIN server... \n");

		myevent_wait(pp_user[user_id].session_login.event_login_req);
	}

	// connect
	DEBUGT2("conn to LOGIN server... \n");
	LOGT4("conn to LOGIN server... \n");

	if(myssl_connect(channel_id, server) < 0 ){
		myssl_close(channel_id);
		return -1;
	}

	// write
	DEBUGT2("send to LOGIN server... \n");
	LOGT4("send to LOGIN server... \n");

	myssl_datawrite(channel_id, proto, strlen(proto));
	DEBUGP2("%s\n", proto);
	LOGT4("datawrite done:\n");
	LOGP4("%s\n", proto);
	LOGT4("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// read 
	DEBUGT2("recv from LOGIN server... \n");
	LOGT4("recv from LOGIN server... \n");

	memset(buff, 0, sizeof(buff));
	int ret = 0; 
	int rcv = 0;
	do{
		ret = myssl_dataread(channel_id, buff + rcv, sizeof(buff) - rcv);
		if(ret < 0) {
			DEBUGP2("myssl_dataread error in proc_login\n");
			LOGT4("myssl_dataread error in proc_login\n");
			myssl_close(channel_id);
			return -1;
		}
		rcv += ret;
	} while(ret !=0 && rcv < sizeof(buff));
	buff[sizeof(buff)-1] = 0;

	DEBUGP2("%s\n", buff);
	LOGT4("dataread done:\n");
	LOGP4("%s\n", buff);
	LOGT4("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// parse
	proto_parselogin(buff, result_login);

	myevent_set(pp_user[user_id].session_login.event_login_ack);		// 登录完成

	// done
	myssl_close(channel_id);

	return 0;
}

int proc_image(int user_id, int bid_id, int delay)
{
	int             group		= pp_user[user_id].group;
	unsigned int    bidnumber	= pp_user[user_id].bidnumber;
	unsigned int    bidpassword	= pp_user[user_id].bidpassword;
	char*           sessionid	= pp_user[user_id].session_login.result_login.sid;	// 应该无用
	RESULT_IMAGE*   result_image	= &pp_user[user_id].session_bid[bid_id].result_image;
	unsigned int 	bidamount	= 0;

	int channel_id 			=-1 ;
	int server			=-1 ;	
	char proto[SEND_BUFF_SIZE] 	={0};
	char buff[RECV_BUFF_SIZE]  	={0};

	if(group == 0)
		server = TOUBIAO_A;
	else
		server = TOUBIAO_B;

	channel_id = channel_findfree();

	// connect
	DEBUGT2("conn to IMAGE server... \n");
	LOGT4("conn to IMAGE server... \n");

	if(myssl_connect(channel_id, server) < 0 ){
		myssl_close(channel_id);
		return -1;
	}

	if(delay != 0 && pp_user[user_id].session_bid[bid_id].event_image_req != NULL){
		DEBUGT2("wait for sent to IMAGE server... \n");
		LOGT4("wait for sent to IMAGE server... \n");

		myevent_wait(pp_user[user_id].session_bid[bid_id].event_image_req);
	}

	switch(bid_id) {
		case 0:
			bidamount 	= user_price0;
			break;
		case 1:
			bidamount	= user_price1;
			break;
		case 2:
			bidamount	= user_price2;
			break;
		default:
			bidamount	= user_price1;
	}

	pp_user[user_id].price[bid_id]	= bidamount;

	memset(proto, 0, sizeof(proto));
	proto_makeimage(								// 先wait后造协议是为了取更加新的价格
			group,
			bidnumber,
			bidpassword,
			bidamount,
			sessionid,
			proto);

	// write
	DEBUGT2("send to IMAGE server... \n");
	LOGT4("send to IMAGE server... \n");

	myssl_datawrite(channel_id, proto, strlen(proto));
	DEBUGP2("%s\n", proto);
	LOGT4("datawrite done:\n");
	LOGP4("%s\n", proto);
	LOGT4("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// read 
	DEBUGT2("recv from IMAGE server... \n");
	LOGT4("recv from IMAGE server... \n");

	memset(buff, 0, sizeof(buff));
	int ret = 0; 
	int rcv = 0;
	do{
		ret = myssl_dataread(channel_id, buff + rcv, sizeof(buff) - rcv);
		if(ret < 0) {
			DEBUGP2("myssl_dataread error in proc_image\n");
			LOGT4("myssl_dataread error in proc_image\n");
			myssl_close(channel_id);
			return -1;
		}
		rcv += ret;
	} while(ret !=0 && rcv < sizeof(buff));
	buff[sizeof(buff)-1] = 0;

	DEBUGP2("%s\n", buff);
	LOGT4("dataread done:\n");
	LOGP4("%s\n", buff);
	LOGT4("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// parse
	proto_parseimage(buff, result_image); 

	//myevent_set(pp_user[user_id].session_bid[bid_id].event_image_ack);		// 验证码请求完成信号放到解码函数中

	// done
	myssl_close(channel_id);

	return 0;
}

int proc_price(int user_id, int bid_id, int delay)
{
	int 		group		= pp_user[user_id].group;
	unsigned int 	bidnumber	= pp_user[user_id].bidnumber;
	unsigned int 	bidpassword	= pp_user[user_id].bidpassword;
	unsigned int 	bidamount	= pp_user[user_id].price[bid_id];
	unsigned int 	imagenumber	= pp_user[user_id].session_bid[bid_id].image;
	char* 		machinecode	= pp_user[user_id].machinecode;
	char* 		sessionid	= pp_user[user_id].session_bid[bid_id].result_image.sid;
	RESULT_PRICE*   result_price	= &pp_user[user_id].session_bid[bid_id].result_price;

	int channel_id 			=-1 ;
	int server			=-1 ;	
	char proto[SEND_BUFF_SIZE] 	={0};
	char buff[RECV_BUFF_SIZE]  	={0};

	if(group == 0)
		server = TOUBIAO_A;
	else
		server = TOUBIAO_B;

	channel_id = channel_findfree();

	// connect
	DEBUGT2("conn to PRICE server... \n");
	LOGT4("conn to PRICE server... \n");

	if(myssl_connect(channel_id, server) < 0 ){
		myssl_close(channel_id);
		return -1;
	}

	if(delay != 0 && pp_user[user_id].session_bid[bid_id].event_image_ack != NULL){
		DEBUGT2("wait for sent to PRICE server... \n");
		LOGT4("wait for sent to PRICE server... \n");

		myevent_wait(pp_user[user_id].session_bid[bid_id].event_image_ack);	// 等待图片解码成功
	}

	memset(proto, 0, sizeof(proto));
	proto_makeprice(								// 先wait后造协议是为了取更加新的价格
			group,
			bidnumber,
			bidpassword,
			bidamount,
			imagenumber,
			machinecode,
			sessionid,
			proto);

	// write
	DEBUGT2("send to PRICE server... \n");
	LOGT4("send to PRICE server... \n");

	myssl_datawrite(channel_id, proto, strlen(proto));
	DEBUGP2("%s\n", proto);
	LOGT4("datawrite done:\n");
	LOGP4("%s\n", proto);
	LOGT4("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// read 
	DEBUGP2("recv from PRICE server... \n");
	LOGT4("recv from PRICE server... \n");

	memset(buff, 0, sizeof(buff));
	int ret = 0; 
	int rcv = 0;
	do{
		ret = myssl_dataread(channel_id, buff + rcv, sizeof(buff) - rcv);
		if(ret < 0) {
			DEBUGP2("myssl_dataread error in proc_price\n");
			LOGT4("myssl_dataread error in proc_price\n");
			myssl_close(channel_id);
			return -1;
		}
		rcv += ret;
	} while(ret !=0 && rcv < sizeof(buff));
	buff[sizeof(buff)-1] = 0;

	DEBUGP2("%s\n", buff);
	LOGT4("dataread done:\n");
	LOGP4("%s\n", buff);
	LOGT4("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// parse
	proto_parseprice(buff, result_price);

	myevent_set(pp_user[user_id].session_bid[bid_id].event_price_ack);		// 设置完成信号

	// done
	myssl_close(channel_id);

	return 0;
}


int proc_decode_connect(void)
{


	return 2014;
}

int proc_decode_close(int dm_fd)
{
	if(dm_fd < 1) {
		return -1;
	}

	//

	return 0;
}

int proc_decode(int user_id, int bid_id, int dm_fd)
{
	int fd = dm_fd;

	if(fd < 1) {
		fd = proc_decode_connect();
	}

	if(fd < 1) {
		return -1;
	}

	//
	pp_user[user_id].session_bid[bid_id].image  = myrand_getint(999999 - 100000);

	myevent_set(pp_user[user_id].session_bid[bid_id].event_image_ack);		// 验证码请求完成并解码完成

	proc_decode_close(dm_fd);

	return 0;
}


int proc_login_udp(int user_id, int option)
{

	return 0;
}

void proc_status_udp(int user_id, int option)
{
	while(flag_login_quit == 0) {
		sleep(1);
	}
}


int proc_logout_udp(int user_id, int option)
{

	return 0;
}

void proc_trigger(void)
{
	while(flag_trigger_quit == 0) {
		sleep(1);
	}
}

