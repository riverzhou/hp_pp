
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
#include "server.h"
#include "proc.h"
#include "user.h"
#include "myevent.h"
#include "ppthread.h"
#include "myxml.h"

// DEBUGP1

//================================================================

//-----------------------------------------------------------------

void main_init(void)
{				// 顺序很重要
	log_init();
	myxml_init();

	server_init();
	myssl_init();
	myrand_init();
	user_init();
}

void main_close(void)
{				// 顺序很重要
	user_clean();
	myssl_clean();
	myxml_clean();
	log_close();
}

// ---------------------------------------------------------

// ---------------------------------------------------------

int main_start_client(int user_id)
{
	pp_user[user_id].arg_client.user_id  	= user_id;
	pp_user[user_id].arg_client.event    	= NULL;

	pthread_create(&(pp_user[user_id].pid_client), NULL, ppthread_client, &(pp_user[user_id].arg_client)); 

	return 0;
}

void main_signal(void)
{
#if 1
	int t = 5 ;

	sleep(t);

	myevent_set(ev_login_start);			// *** 开始登录

	sleep(t);

	myevent_set(ev_first_begin);			// 上半场开始

	sleep(t);

	user_price0 = 500;	 			// 设置上半场价格

	sleep(t);

	myevent_set(ev_bid0_image_shoot); 		// *** 开始上半场出价

	sleep(t);

	myevent_set(ev_second_begin);			// 下半场开始

	sleep(t);

	myevent_set(ev_bid1_image_warmup);		// *** 开始第一次出价预热_图片

	myevent_set(ev_bid1_price_warmup);		// *** 开始第一次出价预热_价格

	myevent_set(ev_bid2_image_warmup);		// *** 开始第二次出价预热_图片

	myevent_set(ev_bid2_price_warmup);		// *** 开始第二次出价预热_价格

	sleep(t);

	user_price1 = 74500;				// 设置第一次出价的价格

	user_price2 = 74600;				// 设置第二次出价的价格

	myevent_set(ev_bid1_image_shoot);		// *** 开始第一次出价_图片

	myevent_set(ev_bid2_image_shoot); 		// *** 开始第二次出价_图片

	sleep(t);

	DEBUGP1("\n发出login和trigger退出信号\n\n");

	flag_login_quit 	= 1;
	flag_trigger_quit 	= 1;
	myevent_set(ev_second_end);			// 全场结束
#endif	
}


int main(int argc, char** argv)
{
	main_init();

	sleep(2);

	flag_login_quit 	= 0;			// 设置退出信号为0
	flag_trigger_quit 	= 0;			// 设置退出信号为0

	int user = user_amount ;

	for(int i = 0; i < user; i++) {
		main_start_client(i);
	}

	main_signal();					// 开始模拟各种事件

//	for(int i = 0; i < user; i++) {
//		user_print(i);
//	}

	for(int i = 0; i < user; i++) {
		pthread_join(pp_user[i].pid_client, NULL); 
	}

	main_close();

	return 0;
}

