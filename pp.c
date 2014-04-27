
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

//#include <errno.h>
//#include <ctype.h>
//#include <openssl/md5.h>

#include <pthread.h>

#include "myrand.h"
#include "log.h"  
#include "myssl.h"  
#include "myudp.h"  
//#include "proto_checkcode.h"  
#include "proto_make.h"  
#include "server.h"
#include "proc.h"
#include "user.h"

// DEBUGP1

//================================================================

//-----------------------------------------------------------------

void main_init(void)
{				// 顺序很重要
	log_init();
	server_init();
	myssl_init();
	myrand_init();
	user_init();
}

void main_close(void)
{
	log_close();
}

// ---------------------------------------------------------

int bid_login(int user_id)
{
	proc_login(
			pp_user[user_id].group,
			pp_user[user_id].bidnumber,
			pp_user[user_id].bidpassword,
			pp_user[user_id].session_login.image,
			pp_user[user_id].machinecode,
			&pp_user[user_id].session_login.result_login);
	return 	0;
}


int bid_nodelay(int user_id, int feq)
{
	proc_image(
			pp_user[user_id].group,
			pp_user[user_id].bidnumber,
			pp_user[user_id].bidpassword,
			pp_user[user_id].price[feq],
			pp_user[user_id].session_login.result_login.sid,		// 应该无用
			&pp_user[user_id].session_bid[feq].result_image,
			NULL);

	proc_decode(
			pp_user[user_id].session_bid[feq].result_image.pic, 
			&pp_user[user_id].session_bid[feq].image,
			NULL);

	proc_price(
			pp_user[user_id].group,
			pp_user[user_id].bidnumber,
			pp_user[user_id].bidpassword,
			pp_user[user_id].price[feq],
			pp_user[user_id].session_bid[feq].image,
			pp_user[user_id].machinecode,
			pp_user[user_id].session_bid[feq].result_image.sid,
			&pp_user[user_id].session_bid[feq].result_price,
			NULL);
	return 	0;
}

// ---------------------------------------------------------
#if 0

void bid_image1(int user_id)
{
	proc_image(
			pp_user[user_id].group,
			pp_user[user_id].bidnumber,
			pp_user[user_id].bidpassword,
			pp_user[user_id].price1,
			pp_user[user_id].sessionid1_image,
			NULL);

}

void bid_price1(int user_id)
{
	proc_price(
			pp_user[user_id].group,
			pp_user[user_id].bidnumber,
			pp_user[user_id].bidpassword,
			pp_user[user_id].price1,
			pp_user[user_id].imagenumber1,
			pp_user[user_id].machinecode,
			pp_user[user_id].sessionid1_price,
			pp_user[user_id].event1_price);

}

EVENT BID_PROC1;
EVENT BID_PROC2;

EVENT BID_CHIELD1;
EVENT BID_CHILED2;

void bid_proc1(int user_id)
{
	pthread_cond_wait(BID_CHIELD1.cond, BID_CHIELD1.mutex);	// 创建子线程，开始预热SSL连接

	if( pthread_create( &(pp_user[user_id].thread_image1_id), NULL , bid_image1, NULL ) ) {
		perror("bid_proc1 pthread create");
		LOGT1("bid_proc1 pthread create\n");
	}

	if( pthread_create( &(pp_user[user_id].thread_price1_id), NULL , bid_price1, NULL ) ) {
		perror("bid_proc1 pthread create");
		LOGT1("bid_proc1 pthread create\n");
	}

	pthread_cond_wait(pp_user[user_id].event1_number->cond, pp_user[user_id].event1_number->mutex);	// 图片解码成功

	pthread_cond_wait(BID_PROC1->cond, BID_PROC1->mutex);	// 策略1信号启动

	pthread_cond_broadcast(pp_user[user_id].event1_price->cond);

}



int bid_delay(int user_id, int n)
{

	if( pthread_create( &(pp_user[user_id].thread_proc1_id), NULL , bid_proc1, NULL ) ) {
		perror("bid_proc1 pthread create");
		LOGT1("bid_proc1 pthread create\n");
	}
#if 0
	if( pthread_create( &(pp_user[user_id].thread_proc2_id), NULL , bid_proc2, NULL ) ) {
		perror("bid_proc2 pthread create");
		LOGT1("bid_proc2 pthread create\n");
	}
#endif
	return 	0;
}

#endif

// ---------------------------------------------------------

int main(int argc, char** argv)
{
	main_init();

	int user_id = myrand_getint(user_amount - 1) ;

	bid_login(user_id);

	bid_nodelay(user_id, 0);

	bid_nodelay(user_id, 1);

	bid_nodelay(user_id, 2);

	user_print(user_id);

	main_close();

	return 0;
}

