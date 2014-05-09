
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <string.h>

#include "myevent.h"
#include "ppthread.h"
#include "user.h"
#include "proc.h"
#include "log.h"


// ====================================================================

void ppthread_image(int user_id, int bid_id)
{
	if(pp_user[user_id].session_bid[bid_id].event_image_prereq != NULL) {
		myevent_wait(pp_user[user_id].session_bid[bid_id].event_image_prereq); 	// 等待验证码图片请求的预热信号
	}

	int dm_fd = 0;									// 连接dm服务器的socket句柄

	dm_fd = proc_decode_connect();							// 连接解码服务器，预连接

	proc_image(user_id, bid_id, 1); 						// 获取验证码图片，开始预热，正式请求由事件触发。阻塞等待返回。第三个参数为是否预热

	proc_decode(user_id, bid_id, dm_fd);						// 向解码服务器发送验证码图片，阻塞等待返回解码结果
}

void ppthread_price(int user_id, int bid_id)
{
	if(pp_user[user_id].session_bid[bid_id].event_price_prereq != NULL) {
		myevent_wait(pp_user[user_id].session_bid[bid_id].event_price_prereq); 	// 等待出价请求的预热信号
	}

	proc_price(user_id, bid_id, 1); 						// 出价，先预热，正式出价请求由事件触发。阻塞等待返回。第三个参数为是否预热
}

// --------------------------------------------------------------------

void *ppthread_image1(void* arg_thread)
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	if(arg->event != NULL) {
		myevent_wait(arg->event);                                 		// 等待激活信号
	}

	ppthread_image(arg->user_id, 1);						// 第二个参数为bid线程号

	pthread_exit(NULL);								// 线程自然退出
	return NULL;
}

void *ppthread_price1(void* arg_thread)
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	if(arg->event != NULL) {
		myevent_wait(arg->event);         					// 等待激活信号
	}

	ppthread_price(arg->user_id, 1);						// 第二个参数为bid线程号

	pthread_exit(NULL);								// 线程自然退出
	return NULL;
}

void *ppthread_image2(void* arg_thread)
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	if(arg->event != NULL) {
		myevent_wait(arg->event);                                 		// 等待激活信号
	}

	ppthread_image(arg->user_id, 2);						// 第二个参数为bid线程号

	pthread_exit(NULL);                                                             // 线程自然退出
	return NULL;
}

void *ppthread_price2(void* arg_thread)
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	if(arg->event != NULL) {
		myevent_wait(arg->event);                              			// 等待激活信号
	}

	ppthread_price(arg->user_id, 2);						// 第二个参数为bid线程号

	pthread_exit(NULL);                                                             // 线程自然退出
	return NULL;
}

// --------------------------------------------------------------------

void *ppthread_login(void* arg_thread)							// 每个程序有一个私有的login线程
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	myevent_wait(ev_login_start);                                                 	// 等待许可登录的信号，全局信号

	proc_login(arg->user_id, 0);							// 处理登录过程的SSL部分

	proc_login_udp(arg->user_id, 0);						// 处理登录过程的UDP部分

	// myevent_set(pp_user[arg->user_id].session_login.event_login_ack); 		// 登录成功 // 改到 proc_login_udp 里处理

	proc_status_udp(arg->user_id, 0);						// 一个带flag_login_quit退出信号变量和sleep(0)的死循环，监控server发回的UDP信息

	proc_logout_udp(arg->user_id, 0);						// 处理退出过程的UDP部分

	pthread_exit(NULL);								// 使用信号变量，自然方式退出
	return NULL;
}

void *ppthread_bid0(void* arg_thread)							// 上半场出价线程
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	if(arg->event != NULL) {
		myevent_wait(arg->event);						// 等待激活信号
	}

	if(pp_user[arg->user_id].session_bid[0].event_image_req!= NULL) {
		myevent_wait(pp_user[arg->user_id].session_bid[0].event_image_req);    	// 等待上半场出价信号
	}

	proc_image(arg->user_id, 0, 0);							// 获取验证码图片，参数NULL表示立即执行不预热。阻塞等待返回。第三个参数为是否预热

	proc_decode(arg->user_id, 0, 0);						// 解码验证码图片，阻塞等待返回。

	proc_price(arg->user_id, 0, 0);			 				// 出价，参数NULL表示立即执行不预热。阻塞等待返回。第三个参数为是否预热

	pthread_exit(NULL);								// 完成出价后线程自然退出
	return NULL;
}

void *ppthread_bid1(void* arg_thread)							// 下板场出价线程1，使用策略1
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	ARG_THREAD 	arg_image;  
	ARG_THREAD 	arg_price;  

	if(arg->event != NULL) {
		myevent_wait(arg->event);						// 等待激活信号
	}

	arg_image.user_id   = arg->user_id;
	arg_image.event     = NULL;							// 子线程激活信号，目前设置为立即激活

	arg_price.user_id   = arg->user_id;						
	arg_price.event     = NULL;							// 子线程激活信号，目前设置为立即激活

	pthread_t pid_image = 0;
	pthread_t pid_price = 0;

	pthread_create(&pid_image, NULL, ppthread_image1, &arg_image); 			// 启动验证码请求与解码线程(目前线程启动时间为下半场开始后)
	pthread_create(&pid_price, NULL, ppthread_price1, &arg_price); 			// 启动出价线程(目前线程启动时间为下半场开始后)

	pthread_join(pid_price,  NULL);                               			// 确认出价线程已退出
	pthread_join(pid_image,  NULL);                               			// 确认验证码线程已退出

	pthread_exit(NULL);								// 完成出价后线程自然退出
	return NULL;
}

void *ppthread_bid2(void* arg_thread)							// 下半场出价线程2，使用策略2
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	ARG_THREAD 	arg_image;  
	ARG_THREAD 	arg_price;  

	if(arg->event != NULL) {
		myevent_wait(arg->event);						// 等待激活信号
	}

	arg_image.user_id   = arg->user_id;
	arg_image.event     = NULL;							// 子线程激活信号，目前设置为立即激活

	arg_price.user_id   = arg->user_id;						
	arg_price.event     = NULL;							// 子线程激活信号，目前设置为立即激活

	pthread_t pid_image = 0;
	pthread_t pid_price = 0;

	pthread_create(&pid_image, NULL, ppthread_image2, &arg_image); 			// 启动验证码请求与解码线程(目前线程启动时间为下半场开始后)
	pthread_create(&pid_price, NULL, ppthread_price2, &arg_price); 			// 启动出价线程(目前线程启动时间为下半场开始后)

	pthread_join(pid_price,  NULL);                               			// 确认出价线程已退出
	pthread_join(pid_image,  NULL);                               			// 确认验证码线程已退出

	pthread_exit(NULL);
	return NULL;
}

// --------------------------------------------------------------------

void *ppthread_trigger(void* arg_thread)						// 整个程序公用一个trigger线程
{
//	ARG_THREAD *arg = (ARG_THREAD*)arg_thread;

	proc_trigger();									// 一个带flag_trigger_quit退出信号变量和sleep(0)的死循环，监控server发回的UDP信息

	DEBUGT1("ppthread_trigger quit\n");

	pthread_exit(NULL);								// 使用信号变量，自然方式退出
	return NULL;
}

void *ppthread_client(void* arg_thread)							// 每个客户使用一个私有的client线程
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	ARG_THREAD 	    arg_login;  
	ARG_THREAD 	    arg_bid0;  
	ARG_THREAD 	    arg_bid1;  
	ARG_THREAD 	    arg_bid2;  

	arg_login.user_id   = arg->user_id;
	arg_login.event     = NULL;

	arg_bid0.user_id    = arg->user_id;
	arg_bid0.event      = NULL;

	arg_bid1.user_id    = arg->user_id;
	arg_bid1.event      = NULL;							

	arg_bid2.user_id    = arg->user_id;
	arg_bid2.event      = NULL;							

	pthread_t pid_login = 0;
	pthread_t pid_bid0  = 0;
	pthread_t pid_bid1  = 0;
	pthread_t pid_bid2  = 0;


	pthread_create(&pid_login, NULL, ppthread_login, &arg_login);			// 先启动登录线程

	myevent_wait(pp_user[arg->user_id].session_login.event_login_ack); 		// 等待登录成功

	myevent_wait(ev_first_begin);							// 等待上半场开始

	pthread_create(&pid_bid0, NULL, ppthread_bid0, &arg_bid0);			// 上半场开始后，启动上半场投标线程

	myevent_wait(ev_second_begin);							// 等待下半场开始

	pthread_create(&pid_bid1, NULL, ppthread_bid1, &arg_bid1);			// 下半场开始后，启动投标线程1
	pthread_create(&pid_bid2, NULL, ppthread_bid2, &arg_bid2);			// 下半场开始后，启动投标线程2

	myevent_wait(ev_second_end);							// 全场结束
	DEBUGT1("client %d : 收到全场结束信号\n", arg->user_id);

	pthread_join(pid_bid0, 	NULL);							// 确认bid0线程已退出
	DEBUGT1("client %d : bid0退出\n", arg->user_id);

	pthread_join(pid_bid1, 	NULL);							// 确认bid1线程已退出
	DEBUGT1("client %d : bid1退出\n", arg->user_id);

	pthread_join(pid_bid2, 	NULL);							// 确认bid2线程已退出
	DEBUGT1("client %d : bid2退出\n", arg->user_id);

	pthread_join(pid_login, NULL);							// 确认login线程已退出
	DEBUGT1("client %d : login退出\n", arg->user_id);

	DEBUGT1("client %d : 正常退出\n", arg->user_id);

	pthread_exit(NULL);								// 使用自然方式退出
	return NULL;
}

// --------------------------------------------------------------------


