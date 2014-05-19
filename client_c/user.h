
#ifndef USER_H_INCLUDED
#define USER_H_INCLUDED

#include <pthread.h>

#include "myevent.h"
#include "ppthread.h"

#define USER_FILE		"/user.xml"

#define MAX_USER		512

#define MAX_IMAGELEN		4096

//=============================================================

typedef struct {
	char number[20];
	char pass[10];
} USER_DICT;

//-------------------------------------------------------------

typedef struct {
	/*
	   JSESSIONID		8899CF08D15BE46A7872A443D865A5D5
	   CLIENTNAME 		ZhangSan
	   PID			332627197611242029
	   */
	char            	sid[128];
	char			name[64];
	char			pid[64];
}RESULT_LOGIN;

typedef struct {
	/*
	   JSESSIONID		8899CF08D15BE46A7872A443D865A5D5
	   ERRORCODE 		0
	   ERRORSTRING		OK！
	   IMAGE_CONTENT	xxxxxx...
	   */
	char            	sid[128];
	char            	errcode[8];
	char            	errstr[128];
	char			pic_64[MAX_IMAGELEN];
	char			pic_bin[MAX_IMAGELEN];
}RESULT_IMAGE;

typedef struct {
	/*
	   JSESSIONID		8899CF08D15BE46A7872A443D865A5D5
	   CLIENTNAME		ZhangSan
	   PID			332627197611242029
	   BIDNUMBER		52203709
	   BIDCOUNT		1
	   BIDAMOUNT		200
	   BIDTIME		2014-04-19 10:42:20
	   */
	char            	sid[128];
	char            	name[64];
	char            	pid[64];
	char			number[16];
	char			count[16];
	char			price[32];
	char			time[32];
}RESULT_PRICE;

typedef struct {
	char			type[256];
	char			val1[256];		// TODO
	char			val2[256];		// TODO
	char			val3[256];		// TODO
	char			val4[256];		// TODO
	char			val5[256];		// TODO
	char			val6[256];		// TODO
	char			val7[256];		// TODO
	char			val8[256];		// TODO
}RESULT_UDP;	

typedef struct {
	volatile unsigned int  	image;
	RESULT_LOGIN		result_login;
	EVENT* 			event_login_req;	// 开始登录
	EVENT*			event_login_ack;	// 登录成功确认
	EVENT			_event_login_ack;	// 私有的ack存储空间，初始化时将指针指入，访问由指针访问
}SESSION_LOGIN;

typedef struct {
	volatile unsigned int 	image;			// 图片解码结果
	RESULT_IMAGE		result_image;
	RESULT_PRICE		result_price;
	EVENT* 			event_image_prereq;	// 发送图片请求预热
	EVENT* 			event_image_req;	// 发送图片请求
	EVENT* 			event_image_ack;	// 得到图片确认
	EVENT*			event_price_prereq;	// 发送出价请求预热
	EVENT*			event_price_ack;	// 出价成功确认
	EVENT			_event_image_ack;	// 私有的ack存储空间，初始化时将指针指入，访问由指针访问
	EVENT			_event_price_ack;	// 私有的ack存储空间，初始化时将指针指入，访问由指针访问
}SESSION_BID;

typedef struct {
	int 			fd;
	int 			flag_nodata;
	int			flag_timeout;
	RESULT_UDP		result_udp;
}SESSION_UDP;

//-------------------------------------------------------------

typedef struct {
	int			flag_running;

	int             	group;
	char 	        	machinecode[256];
	unsigned int    	bidnumber;
	unsigned int    	bidpassword;

	volatile unsigned int	price[3];

	pthread_t		pid_client;
	ARG_THREAD		arg_client;

	SESSION_UDP		session_udp;
	SESSION_LOGIN		session_login;
	SESSION_BID		session_bid[3];

} PP_USER ;

//=============================================================
extern volatile unsigned int 	flag_login_quit;	// login线程退出信号
extern volatile unsigned int 	flag_trigger_quit;	// trigger线程退出信号

extern volatile unsigned int   	user_amount ;     	// 用户数，从xml配置文件中统计得到

extern volatile unsigned int   	user_price0 ;         	// 上半场的投标价格
extern volatile unsigned int   	user_price1 ;         	// 下半场的策略1的投标价格
extern volatile unsigned int   	user_price2 ;         	// 下半场的策略2的投标价格

extern EVENT*			ev_login_start;		// 开始登录
extern EVENT*			ev_first_begin;		// 上半场开始
extern EVENT*			ev_second_begin;	// 下半场开始
extern EVENT*			ev_second_end;		// 全场结束
extern EVENT*			ev_bid0_image_shoot;	// 上半场出价
extern EVENT*			ev_bid1_image_shoot;	// 下半场策略1出价
extern EVENT*			ev_bid1_image_warmup;	// 下半场策略1预热
extern EVENT*			ev_bid1_price_warmup;	// 下半场策略1预热
extern EVENT*			ev_bid2_image_shoot;	// 下半场策略2出价
extern EVENT*			ev_bid2_image_warmup;	// 下半场策略2预热
extern EVENT*			ev_bid2_price_warmup;	// 下半场策略2预热

extern PP_USER        		pp_user[MAX_USER];	// 用户数据中心

//-------------------------------------------------------------

int user_init(void);
void user_clean(void);

int user_print(int user_id);

//=============================================================

#endif // USER_H_INCLUDED

