
#ifndef DM_CLIENT_H_INCLUDED
#define DM_CLIENT_H_INCLUDED

#define MAX_IMAGELEN    4096

//---------------------------------------------
#if 0
//---------------------------------------------

typedef struct{
	unsigned short  priority;
	unsigned short  userid;
	unsigned int    imagelen;
	unsigned char   image[MAX_IMAGELEN];
} PROTO_SEND;

typedef struct{
	unsigned int    number;
} PROTO_RECV;

//---------------------------------------------
#endif
//---------------------------------------------

#define DM_PROTO_ID                     10000

#pragma pack (2)                        //指定按2字节对齐
typedef struct {                        //请求协议包  //4,2,4
	int     nTotalLen;              //总长度,不包括自己的4个字节
	short   nProtocolID;            //协议ID,Request是10000
	int     nBodyLen;               //数据体的长度,即ImageCode JPG内容的长度
	char    arBody[MAX_IMAGELEN];   //ImageCode JPG内容
} PROTO_SEND;

typedef struct {                        //返回协议包
	int     nTotalLen;              //总长度,不包括自己的4个字节
	short   nProtocolID;            //协议ID,response是10001
	int     nBodyLen;               //数据体的长度,即=4
	int     nCodeNum;               //图形码数值
} PROTO_RECV;
#pragma pack ()                         //取消指定对齐，恢复缺省对齐

//---------------------------------------------

//#define DM_SERVER_PORT     		9999
//#define DM_SERVER_IP       		"127.0.0.1"

//#define DM_SERVER_PORT     		2000
//#define DM_SERVER_IP       		"192.168.1.112"

//int dm_connect(void);

//int dm_64_to_bin(char* pic_64, char* pic_bin);

//unsigned int dm_getimage(int fd, int user_id, char* pic_bin, int len);


#endif // DM_CLIENT_H_INCLUDED

