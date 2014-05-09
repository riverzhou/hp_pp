
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <string.h>

#include "myevent.h"
#include "ppthread.h"


// ====================================================================

// --------------------------------------------------------------------

void *ppthread_image1(void* arg_thread)
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	if(arg->event != NULL) {
		event_wait(arg->event);                                 		// 等待激活信号
	}

	if(pp_user[arg->user_id].session_bid[1].event_image_prereq != NULL) {
		event_wait(pp_user[arg->user_id].session_bid[1].event_image_prereq); 	// 等待验证码图片请求的预热信号
	}

	int dm_fd = 0;									// 连接dm服务器的socket句柄

	proc_image_decode_connect(arg->user_id, &dm_fd);				// 连接解码服务器，预连接

	proc_image(arg->user_id, pp_user[arg->user_id].session_bid[1].event_image_req);	// 获取验证码图片，开始预热，正式请求由事件触发。阻塞等待返回

	proc_image_decode(arg->user_id, dm_fd);	                                	// 向解码服务器发送验证码图片，阻塞等待返回解码结果

	myevent_set(pp_user[arg->user_id].session_bid[1].event_image_ack);		// 验证码图片获得完成并且解码完成

	pthread_exit(NULL);								// 线程自然退出
	return NULL;
}

void *ppthread_price1(void* arg_thread)
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	if(arg->event != NULL) {
		event_wait(arg->event);                                                 // 等待激活信号
	}

	if(pp_user[arg->user_id].session_bid[1].event_price_prereq != NULL) {
		event_wait(pp_user[arg->user_id].session_bid[1].event_price_prereq);    // 等待出价请求的预热信号
	}

	proc_price(arg->user_id, pp_user[arg->user_id].session_bid[1].event_price_req);	// 出价，先预热，正式出价请求由事件触发。阻塞等待返回

	myevent_set(pp_user[arg->user_id].session_bid[1].event_price_ack);              // 出价请求完成

	pthread_exit(NULL);								// 线程自然退出
	return NULL;
}

void *ppthread_image2(void* arg_thread)
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	if(arg->event != NULL) {
		event_wait(arg->event);                                 		// 等待激活信号
	}

	if(pp_user[arg->user_id].session_bid[2].event_image_prereq != NULL) {
		event_wait(pp_user[arg->user_id].session_bid[2].event_image_prereq); 	// 等待验证码图片请求的预热信号
	}

	int dm_fd = 0;									// 连接dm服务器的socket句柄

	proc_image_decode_connect(arg->user_id, &dm_fd);				// 连接解码服务器，预连接

	proc_image(arg->user_id, pp_user[arg->user_id].session_bid[2].event_image_req);	// 获取验证码图片，开始预热，正式请求由事件触发。阻塞等待返回

	proc_image_decode(arg->user_id, dm_fd);	                                	// 向解码服务器发送验证码图片，阻塞等待返回解码结果

	myevent_set(pp_user[arg->user_id].session_bid[2].event_image_ack);		// 验证码图片获得完成并且解码完成

	pthread_exit(NULL);                                                             // 线程自然退出
	return NULL;
}

void *ppthread_price2(void* arg_thread)
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	if(arg->event != NULL) {
		event_wait(arg->event);                                                 // 等待激活信号
	}

	if(pp_user[arg->user_id].session_bid[2].event_price_prereq != NULL) {
		event_wait(pp_user[arg->user_id].session_bid[1].event_price_prereq);    // 等待出价请求的预热信号
	}

	proc_price(arg->user_id, pp_user[arg->user_id].session_bid[2].event_price_req);	// 出价，先预热，正式出价请求由事件触发。阻塞等待返回

	myevent_set(pp_user[arg->user_id].session_bid[2].event_price_ack);              // 出价请求完成

	pthread_exit(NULL);                                                             // 线程自然退出
	return NULL;
}

// --------------------------------------------------------------------

void *ppthread_login(void* arg_thread)							// 每个程序有一个私有的login线程
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	proc_login(arg->user_id);							// 处理登录过程的SSL部分

	proc_login_udp(arg->user_id);							// 处理登录过程的UDP部分

	proc_status_udp(arg->user_id);							// 一个带pthread_testcancel()和sleep(0)的死循环，监控server发回的UDP信息

	proc_logout_udp(arg->user_id);							// 处理退出过程的UDP部分

	pthread_exit(NULL);								// 线程使用pthread_cancel()方式退出
	return NULL;
}

void *ppthread_bid0(void* arg_thread)							// 上半场出价线程
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	if(arg->event != NULL) {
		event_wait(arg->event);							// 等待激活信号
	}

        if(pp_user[arg->user_id].session_bid[0].event_price_req!= NULL) {
                event_wait(pp_user[arg->user_id].session_bid[0].event_price_req);    	// 等待上半场出价信号
        }

	proc_image(arg->user_id, NULL);							// 获取验证码图片，参数NULL表示立即执行不预热。阻塞等待返回

	proc_image_decode(arg->user_id);						// 解码验证码图片，阻塞等待返回。

	proc_price(arg->user_id, NULL);							// 出价，参数NULL表示立即执行不预热。阻塞等待返回

	myevent_set(pp_user[arg->user_id].session_bid[0].event_price_ack); 		// 出价请求完成

	pthread_exit(NULL);								// 完成出价后线程自然退出
	return NULL;
}

void *ppthread_bid1(void* arg_thread)							// 下板场出价线程1，使用策略1
{
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	ARG_THREAD 	arg_image;  
	ARG_THREAD 	arg_price;  

	if(arg->event != NULL) {
		event_wait(arg->event);							// 等待激活信号
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
		event_wait(arg->event);							// 等待激活信号
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
	ARG_THREAD *arg = (ARG_THREAD*)arg_thread ;

	proc_trigger();									// 一个带pthread_testcancel()和sleep(0)的死循环，监控server发回的UDP信息

	pthread_exit(NULL);								// 线程使用pthread_cancel()方式退出
	return NULL;
}

void *ppthread_client(void* arg_thread)							// 每个客户使用一个私有的client线程
{
	ARG_THREAD 	    arg_login;  
	ARG_THREAD 	    arg_bid0;  
	ARG_THREAD 	    arg_bid1;  
	ARG_THREAD 	    arg_bid2;  

	arg_login.user_id   = arg_thread->user_id;
	arg_login.event     = NULL;

	arg_bid0.user_id    = arg_thread->user_id;
	arg_bid0.event      = NULL;

	arg_bid1.user_id    = arg_thread->user_id;
	arg_bid1.event      = NULL;							

	arg_bid2.user_id    = arg_thread->user_id;
	arg_bid2.event      = NULL;							

	pthread_t pid_login = 0;
	pthread_t pid_bid0  = 0;
	pthread_t pid_bid1  = 0;
	pthread_t pid_bid2  = 0;


	pthread_create(&pid_login, NULL, ppthread_login, &arg_login);			// 先启动登录线程

	myevent_wait(EVENT_first_begin);						// 等待上半场开始

	pthread_create(&pid_bid0, NULL, ppthread_bid0, &arg_bid0);			// 上半场开始后，启动上半场投标线程

	myevent_wait(EVENT_second_begin);						// 等待下半场开始

	pthread_create(&pid_bid1, NULL, ppthread_bid1, &arg_bid1);			// 下半场开始后，启动投标线程1
	pthread_create(&pid_bid2, NULL, ppthread_bid2, &arg_bid2);			// 下半场开始后，启动投标线程2

	myevent_wait(EVENT_all_end);							// 全场结束

	pthread_cancel(pid_login);							// 通知login线程退出

	pthread_join(pid_bid0, 	NULL);							// 确认bid0线程已退出
	pthread_join(pid_bid1, 	NULL);							// 确认bid1线程已退出
	pthread_join(pid_bid2, 	NULL);							// 确认bid2线程已退出

	pthread_join(pid_login, NULL);							// 确认login线程已退出


	pthread_exit(NULL);								// 使用自然方式退出
	return NULL;
}

// --------------------------------------------------------------------


