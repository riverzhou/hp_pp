
#ifndef DM_CLIENT_H_INCLUDED
#define DM_CLIENT_H_INCLUDED

#include "user.h"

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

#define DM_SERVER_PORT     9999
#define DM_SERVER_IP       "127.0.0.1"

int dm_connect(void);

int dm_64_to_bin(char* pic_64, char* pic_bin);

unsigned int dm_getimage(int fd, int priority, int userid, char* pic_bin, int len);
	

#endif // DM_CLIENT_H_INCLUDED

