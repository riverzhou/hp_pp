
#ifdef _MINGW_
#include <windows.h>
#else
#include <pthread.h>
#endif

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

// DEBUGP2
// LOGP2

#define SEND_BUFF_SIZE 	4096
#define RECV_BUFF_SIZE  8192

//================================================================
//----------------------------------------------------------------

#ifdef _MINGW_
int proc_wait(EVENT* event)
{
	return 	0;
}
#else
int proc_wait(EVENT* event)
{
	return 	pthread_cond_wait(event->cond, event->mutex);
}
#endif

int proc_login(
		int		group,
		unsigned int	bidnumber,
		unsigned int	bidpassword,
		unsigned int	imagenumber,
		char*		machinecode,
		RESULT_LOGIN* 	result_login)
{
	int channel_id 	=-1 ;
	int server	=-1 ;	
	char proto[SEND_BUFF_SIZE] ={0};
	char buff[RECV_BUFF_SIZE]  ={0};

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

	// connect
	DEBUGT2("conn to LOGIN server... \n");
	LOGT2("conn to LOGIN server... \n");

	if(myssl_connect(channel_id, server) < 0 ){
		myssl_close(channel_id);
		return -1;
	}

	// write
	DEBUGT2("send to LOGIN server... \n");
	LOGT2("send to LOGIN server... \n");

	myssl_datawrite(channel_id, proto, strlen(proto));
	DEBUGP2("%s\n", proto);
	LOGT2("datawrite done:\n");
	LOGP2("%s\n", proto);
	LOGT2("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// read 
        DEBUGT2("recv from LOGIN server... \n");
        LOGT2("recv from LOGIN server... \n");

        memset(buff, 0, sizeof(buff));
	int ret = 0; 
	int rcv = 0;
	do{
		ret = myssl_dataread(channel_id, buff + rcv, sizeof(buff) - rcv);
		if(ret < 0) {
			DEBUGP2("myssl_dataread error in proc_login\n");
			LOGT2("myssl_dataread error in proc_login\n");
			myssl_close(channel_id);
			return -1;
		}
		rcv += ret;
	} while(ret !=0 && rcv < sizeof(buff));
	buff[sizeof(buff)-1] = 0;

	DEBUGP2("%s\n", buff);
	LOGT2("dataread done:\n");
	LOGP2("%s\n", buff);
	LOGT2("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// parse
	proto_parselogin(buff, result_login);

	// done
	myssl_close(channel_id);

	return 0;
}

int proc_image(
		int 		group,
		unsigned int 	bidnumber,
		unsigned int 	bidpassword,
		unsigned int* 	bidamount,
		char* 		sessionid,
		RESULT_IMAGE* 	result_image,
		EVENT*		event)
{
	int channel_id 	=-1 ;
	int server	=-1 ;	
	char proto[SEND_BUFF_SIZE] ={0};
	char buff[RECV_BUFF_SIZE]  ={0};

	if(group == 0)
		server = TOUBIAO_A;
	else
		server = TOUBIAO_B;

	channel_id = channel_findfree();

	// connect
	DEBUGT2("conn to IMAGE server... \n");
	LOGT2("conn to IMAGE server... \n");

	if(myssl_connect(channel_id, server) < 0 ){
		myssl_close(channel_id);
		return -1;
	}

	if(event != NULL){
		DEBUGT2("wait for sent to IMAGE server... \n");
		LOGT2("wait for sent to IMAGE server... \n");

		proc_wait(event);
	}

	memset(proto, 0, sizeof(proto));
	proto_makeimage(
			group,
			bidnumber,
			bidpassword,
			*bidamount,
			sessionid,
			proto);

	// write
	DEBUGT2("send to IMAGE server... \n");
	LOGT2("send to IMAGE server... \n");

	myssl_datawrite(channel_id, proto, strlen(proto));
	DEBUGP2("%s\n", proto);
	LOGT2("datawrite done:\n");
	LOGP2("%s\n", proto);
	LOGT2("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// read 
	DEBUGT2("recv from IMAGE server... \n");
	LOGT2("recv from IMAGE server... \n");

	memset(buff, 0, sizeof(buff));
	int ret = 0; 
	int rcv = 0;
	do{
		ret = myssl_dataread(channel_id, buff + rcv, sizeof(buff) - rcv);
		if(ret < 0) {
			DEBUGP2("myssl_dataread error in proc_image\n");
			LOGT2("myssl_dataread error in proc_image\n");
			myssl_close(channel_id);
			return -1;
		}
		rcv += ret;
	} while(ret !=0 && rcv < sizeof(buff));
	buff[sizeof(buff)-1] = 0;

	DEBUGP2("%s\n", buff);
	LOGT2("dataread done:\n");
	LOGP2("%s\n", buff);
	LOGT2("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// parse
	proto_parseimage(buff, result_image); 

	// done
	myssl_close(channel_id);

	return 0;
}

int proc_price(
		int 		group,
		unsigned int 	bidnumber,
		unsigned int 	bidpassword,
		unsigned int* 	bidamount,
		unsigned int 	imagenumber,
		char* 		machinecode,
		char* 		sessionid,
		RESULT_PRICE*   result_price,
		EVENT*		event)
{
	int channel_id 	=-1 ;
	int server	=-1 ;	
	char proto[SEND_BUFF_SIZE] ={0};
	char buff[RECV_BUFF_SIZE]  ={0};

	if(group == 0)
		server = TOUBIAO_A;
	else
		server = TOUBIAO_B;

	channel_id = channel_findfree();

	// connect
	DEBUGT2("conn to PRICE server... \n");
	LOGT2("conn to PRICE server... \n");

	if(myssl_connect(channel_id, server) < 0 ){
		myssl_close(channel_id);
		return -1;
	}

	if(event != NULL){
		DEBUGT2("wait for sent to IMAGE server... \n");
		LOGT2("wait for sent to IMAGE server... \n");

		proc_wait(event);
	}

	memset(proto, 0, sizeof(proto));
	proto_makeprice(
			group,
			bidnumber,
			bidpassword,
			*bidamount,
			imagenumber,
			machinecode,
			sessionid,
			proto);

	// write
	DEBUGT2("send to PRICE server... \n");
	LOGT2("send to PRICE server... \n");

	myssl_datawrite(channel_id, proto, strlen(proto));
	DEBUGP2("%s\n", proto);
	LOGT2("datawrite done:\n");
	LOGP2("%s\n", proto);
	LOGT2("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// read 
	DEBUGP2("recv from PRICE server... \n");
	LOGT2("recv from PRICE server... \n");

	memset(buff, 0, sizeof(buff));
	int ret = 0; 
	int rcv = 0;
	do{
		ret = myssl_dataread(channel_id, buff + rcv, sizeof(buff) - rcv);
		if(ret < 0) {
			DEBUGP2("myssl_dataread error in proc_price\n");
			LOGT2("myssl_dataread error in proc_price\n");
			myssl_close(channel_id);
			return -1;
		}
		rcv += ret;
	} while(ret !=0 && rcv < sizeof(buff));
	buff[sizeof(buff)-1] = 0;

	DEBUGP2("%s\n", buff);
	LOGT2("dataread done:\n");
	LOGP2("%s\n", buff);
	LOGT2("---------------------------------------------------------------\n");
	DEBUGP2("---------------------------------------------------------------\n");

	// parse
	proto_parseprice(buff, result_price);

	// done
	myssl_close(channel_id);

	return 0;
}

int proc_decode(
		char* 		pic, 
		unsigned int* 	image ,
		EVENT*          event)
{
	return 0;
}


