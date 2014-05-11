
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
#include "dm_client.h"

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
	if(channel_id < 0 ) {
		fprintf(stderr,"%s : channel_findfree error \n", __func__);
		LOGT1("%s : channel_findfree error \n", __func__);
		return -1;
	}

	if(pp_user[user_id].session_login.event_login_req != NULL){
		DEBUGP2("wait for conn to LOGIN server... \n");
		LOGT4("wait for conn to LOGIN server... \n");

		myevent_wait(pp_user[user_id].session_login.event_login_req);
	}

	// connect
	DEBUGP2("conn to LOGIN server... \n");
	LOGT4("conn to LOGIN server... \n");

	if(myssl_connect(channel_id, server) < 0 ){
		fprintf(stderr,"%s : myssl_connect error \n", __func__);
		LOGT1("%s : myssl_connect error \n", __func__);
		myssl_close(channel_id);
		return -1;
	}

	int ret = 0;
	// write
	DEBUGP2("send to LOGIN server... \n");
	LOGT4("send to LOGIN server... \n");

	ret = myssl_datawrite(channel_id, proto, strlen(proto));
	if(ret < 0) {
		fprintf(stderr,"%s : myssl_datawrite error \n", __func__);
		LOGT1("%s : myssl_datawrite error \n", __func__);
		myssl_close(channel_id);
		return -1;
	}

	DEBUGP2("%s\n", proto);
	LOGT4("datawrite done:\n");
	LOGP4("%s\n", proto);
	LOGT4("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// read 
	DEBUGP2("recv from LOGIN server... \n");
	LOGT4("recv from LOGIN server... \n");

	memset(buff, 0, sizeof(buff));
	int rcv = 0;
	do{
		ret = myssl_dataread(channel_id, buff + rcv, sizeof(buff) - rcv);
		if(ret < 0) {
			fprintf(stderr,"%s : myssl_dataread error \n", __func__);
			LOGT1("%s : myssl_dataread error \n", __func__);
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
	if(channel_id < 0 ) {
		fprintf(stderr,"%s : channel_findfree error \n", __func__);
		LOGT1("%s : channel_findfree error \n", __func__);
		return -1;
	}

	// connect
	DEBUGP2("conn to IMAGE server... \n");
	LOGT4("conn to IMAGE server... \n");

	if(myssl_connect(channel_id, server) < 0 ){
		fprintf(stderr,"%s : myssl_connect error \n", __func__);
		LOGT1("%s : myssl_connect error \n", __func__);
		myssl_close(channel_id);
		return -1;
	}

	if(delay != 0 && pp_user[user_id].session_bid[bid_id].event_image_req != NULL){
		DEBUGP2("wait for sent to IMAGE server... \n");
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

	if(bidamount == 0) {
		fprintf(stderr, "%s : bidamount == 0 (get from user_priceX) user_id=%d, bid_id=%d\n", __func__, user_id, bid_id);
		LOGT1("%s : bidamount == 0 (get from user_priceX) user_id=%d, bid_id=%d\n", __func__, user_id, bid_id);
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

	int ret = 0;
	// write
	DEBUGP2("send to IMAGE server... \n");
	LOGT4("send to IMAGE server... \n");

	ret = myssl_datawrite(channel_id, proto, strlen(proto));
	if(ret < 0) {
		fprintf(stderr,"%s : myssl_datawrite error \n", __func__);
		LOGT1("%s : myssl_datawrite error \n", __func__);
		myssl_close(channel_id);
		return -1;
	}

	DEBUGP2("%s\n", proto);
	LOGT4("datawrite done:\n");
	LOGP4("%s\n", proto);
	LOGT4("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// read 
	DEBUGP2("recv from IMAGE server... \n");
	LOGT4("recv from IMAGE server... \n");

	memset(buff, 0, sizeof(buff));
	int rcv = 0;
	do{
		ret = myssl_dataread(channel_id, buff + rcv, sizeof(buff) - rcv);
		if(ret < 0) {
			fprintf(stderr,"%s : myssl_dataread error \n", __func__);
			LOGT1("%s : myssl_dataread error \n", __func__);
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
	unsigned int 	bidamount	= 0;
	unsigned int 	imagenumber	= pp_user[user_id].session_bid[bid_id].image;
	char* 		machinecode	= pp_user[user_id].machinecode;
	char* 		sessionid	= pp_user[user_id].session_bid[bid_id].result_image.sid;
	RESULT_PRICE*   result_price	= &pp_user[user_id].session_bid[bid_id].result_price;

	int channel_id 			=-1 ;
	int server			=-1 ;	
	char proto[SEND_BUFF_SIZE] 	={0};
	char buff[RECV_BUFF_SIZE]  	={0};


	if(group == 0) {
		server = TOUBIAO_A;
	}
	else {
		server = TOUBIAO_B;
	}

	channel_id = channel_findfree();
	if(channel_id < 0 ) {
		fprintf(stderr,"%s : channel_findfree error \n", __func__);
		LOGT1("%s : channel_findfree error \n", __func__);
		return -1;
	}

	// connect
	DEBUGP2("conn to PRICE server... \n");
	LOGT4("conn to PRICE server... \n");

	if(myssl_connect(channel_id, server) < 0 ){
		fprintf(stderr,"%s : myssl_connect error \n", __func__);
		LOGT1("%s : myssl_connect error \n", __func__);
		myssl_close(channel_id);
		return -1;
	}

	if(delay != 0 && pp_user[user_id].session_bid[bid_id].event_image_ack != NULL){
		DEBUGP2("wait for sent to PRICE server... \n");
		LOGT4("wait for sent to PRICE server... \n");

		myevent_wait(pp_user[user_id].session_bid[bid_id].event_image_ack);	// 等待图片解码成功
	}

	bidamount = pp_user[user_id].price[bid_id];
	if(bidamount == 0) {
		fprintf(stderr, "%s : bidamount == 0 : user_id=%d, bid_id=%d\n", __func__, user_id, bid_id);
		LOGT1("%s : bidamount == 0 : user_id=%d, bid_id=%d\n", __func__, user_id, bid_id);
		return -1;
	};

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

	int ret = 0;
	// write
	DEBUGP2("send to PRICE server... \n");
	LOGT4("send to PRICE server... \n");

	ret = myssl_datawrite(channel_id, proto, strlen(proto));
	if(ret < 0) {
		fprintf(stderr,"%s : myssl_datawrite error \n", __func__);
		LOGT1("%s : myssl_datawrite error \n", __func__);
		myssl_close(channel_id);
		return -1;
	}

	DEBUGP2("%s\n", proto);
	LOGT4("datawrite done:\n");
	LOGP4("%s\n", proto);
	LOGT4("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// read 
	DEBUGP2("recv from PRICE server... \n");
	LOGT4("recv from PRICE server... \n");

	memset(buff, 0, sizeof(buff));
	int rcv = 0;
	do{
		ret = myssl_dataread(channel_id, buff + rcv, sizeof(buff) - rcv);
		if(ret < 0) {
			fprintf(stderr,"%s : myssl_dataread error \n", __func__);
			LOGT1("%s : myssl_dataread error \n", __func__);
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

//--------------------------------------------------------------

int proc_decode_connect(void)
{
	return dm_connect();
}

int proc_decode(int user_id, int bid_id, int dm_fd)
{
	int fd = dm_fd;

	if(fd <= 0) {
		fd = dm_connect();
	}

	if(fd <= 0) {
		return -1;
	}

	int len = dm_64_to_bin(	pp_user[user_id].session_bid[bid_id].result_image.pic_64,
				pp_user[user_id].session_bid[bid_id].result_image.pic_bin);

	pp_user[user_id].session_bid[bid_id].image  =
			dm_getimage(fd, 0, user_id, pp_user[user_id].session_bid[bid_id].result_image.pic_bin, len) % 1000000;

	myevent_set(pp_user[user_id].session_bid[bid_id].event_image_ack);		// 验证码请求完成并解码完成

	return 0;
}

//--------------------------------------------------------------

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

//--------------------------------------------------------------

void proc_trigger(void)
{
	while(flag_trigger_quit == 0) {
		sleep(1);
	}
}


