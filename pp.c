
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

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

static char err_client[MAX_USER] ={0};
static int  err_client_amount 	 = 0;

void main_client_waitquit(void)
{
	int retry = 5;
	int cycle = 5;
	int not_quit_yet = 0;

	for(int n = 0; n < retry; n++) {
		sleep(cycle);
		not_quit_yet = 0;
		for(int i = 0; i < user_amount; i++) {
			if(pp_user[i].flag_running != 0) {
				not_quit_yet++;
			}
		}
		DEBUGP1("%d clients not quit yet. \n", not_quit_yet);
		LOGT1("%d clients not quit yet. \n", not_quit_yet);
		if(not_quit_yet == 0 ) {
			break;
		};
	}
}

void main_client_printerror(void)
{

	for(int i = 0; i < user_amount; i++) {
		for(int n = 0; n < 3; n++) {
			if(pp_user[i].price[n] == 0) {
				err_client[i] = 1 ;
				break;
			}

			if(pp_user[i].session_bid[n].event_price_ack->signal == 0) {
				err_client[i] = 2 ;
				break;
			}
		}
	}

	err_client_amount = 0;
	for(int i = 0; i < user_amount; i++) {
		if(err_client[i] != 0) {
			err_client_amount++;
			user_print(i);
		}
	}
	
	DEBUGP1("%d clients error. \n", err_client_amount);
	LOGT1("%d clients error. \n", err_client_amount);
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

	main_client_waitquit();

	main_client_printerror();

	main_close();

	return 0;
}

