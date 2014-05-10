
#ifndef DM_CLIENT_H_INCLUDED
#define DM_CLIENT_H_INCLUDED
//-----------------------------------------------------------------------

#define MAX_IMAGELEN	8192 

typedef struct{
	unsigned short  priority;
	unsigned short  userid;
	unsigned int    imagelen;
	unsigned char   image[MAX_IMAGELEN];
} PROTO_SEND;

typedef struct{
	unsigned int    number;
} PROTO_RECV;


#endif // DM_CLIENT_H_INCLUDED

