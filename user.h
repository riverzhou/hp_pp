
#ifndef USER_H_INCLUDED
#define USER_H_INCLUDED

#ifndef _MINGW_
#include <pthread.h>
#endif

#ifdef _MINGW_
#define USER_FILE	"\\user.xml"
#else
#define USER_FILE	"/user.xml"
#endif

#define MAX_USER	256


unsigned int user_amount;

#ifdef _MINGW_
typedef HANDLE 	EVENT;
#else
typedef struct{
	pthread_cond_t*		cond; 
	pthread_mutex_t*	mutex;
}
EVENT;
#endif

typedef struct {
	/*
	   JSESSIONID		8899CF08D15BE46A7872A443D865A5D5
	   CLIENTNAME 		ZhangSan
	   PID			332627197611242029
	 */
	char            sid[128];
	char		name[64];
	char		pid[64];
}RESULT_LOGIN;

typedef struct {
	/*
	   JSESSIONID		8899CF08D15BE46A7872A443D865A5D5
	   ERRORCODE 		0
	   ERRORSTRING		OK！
	   IMAGE_CONTENT	xxxxxx...
	 */
	char            sid[128];
	char            errcode[8];
	char            errstr[128];
	char		pic[4096];
}RESULT_IMAGE;


typedef struct {
	/*
	   JSESSIONID		8899CF08D15BE46A7872A443D865A5D5
	   CLIENTNAME		ZhangSan
	   PID			332627197611242029
	   BIDNUMBER		52203709
	   BIDCOUNT		1
	   BIDAMOUNT		200
	   BIDTIME			2014-04-19 10:42:20
	 */
	char            sid[128];
	char            name[64];
	char            pid[64];
	char		number[16];
	char		count[16];
	char		price[32];
	char		time[32];
}RESULT_PRICE;


typedef struct {
	unsigned int    image;
	RESULT_LOGIN	result_login;
}SESSION_LOGIN;


typedef struct {
	unsigned int    image;			// 图片解码结果
	RESULT_IMAGE	result_image;
	RESULT_PRICE	result_price;
	EVENT* 		event_image_prereq;	// 发送图片请求预热
	EVENT* 		event_image_req;	// 发送图片请求
	EVENT* 		event_image_ack;	// 得到图片确认
	EVENT*		event_price_prereq;	// 发送出价请求预热
	EVENT*		event_price_req;	// 发送出价请求
	EVENT*		event_price_ack;	// 出价成功确认
	EVENT		_event_image_ack;	// 私有的ack存储空间，初始化时将指针指入，访问由指针访问
	EVENT		_event_price_ack:	// 私有的ack存储空间，初始化时将指针指入，访问由指针访问
}SESSION_BID;

//-------------------------------------------------------------

typedef struct {
	int             group;		

	char 	        machinecode[256];
	unsigned int    bidnumber;
	unsigned int    bidpassword;

	unsigned int*	price[3];		// 第一次出价

	SESSION_LOGIN	session_login;
	SESSION_BID	session_bid[3];

#ifdef _MINGW_

#else
	pthread_t	threadid_proc1;
	pthread_t	threadid_image1;
	pthread_t	threadid_price1;

	pthread_t	threadid_proc2;
	pthread_t	threadid_image2;
	pthread_t	threadid_price2;
#endif	
} PP_USER ;

volatile PP_USER pp_user[MAX_USER];

//-------------------------------------------------------------

int user_init(void);

int user_print(int user_id);

#endif // USER_H_INCLUDED

