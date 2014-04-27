#ifndef SERVER_H_INCLUDED
#define SERVER_H_INCLUDED

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

#define LOGIN_A             	0
#define TOUBIAO_A           	1
#define RESULT_A            	2
#define QUERY_A		    	3
#define UDP_A		    	4	

#define LOGIN_B             	5
#define TOUBIAO_B           	6
#define RESULT_B            	7
#define QUERY_B		    	8
#define UDP_B		    	9	

#define LOGIN_PORT          	443
#define TOUBIAO_PORT        	443
#define RESULT_PORT         	443
#define QUERY_PORT          	80
#define UDP_PORT            	59139

#define LOGIN_SERVER_A      	"tblogin.alltobid.com"
#define TOUBIAO_SERVER_A    	"toubiao.alltobid.com"
#define RESULT_SERVER_A     	"tbresult.alltobid.com"
#define QUERY_SERVER_A	    	"tbquery.alltobid.com"
#define UDP_SERVER_A	    	"tbudp.alltobid.com"

#define LOGIN_SERVER_B      	"tblogin2.alltobid.com"
#define TOUBIAO_SERVER_B    	"toubiao2.alltobid.com"
#define RESULT_SERVER_B     	"tbresult2.alltobid.com"
#define QUERY_SERVER_B	    	"tbquery2.alltobid.com"
#define UDP_SERVER_B	    	"tbudp2.alltobid.com"

#define MAX_SERVER      	12

typedef struct{
	char domain[255];
	unsigned int port;
	struct sockaddr_in addr;
}SERVER ;

SERVER  server[MAX_SERVER];

void server_init(void);

/* *************************************************

https://tbresult.alltobid.com/car/gui/querybid.aspx?
https://tblogin.alltobid.com/car/gui/login.aspx?
https://toubiao.alltobid.com/car/gui/imagecode.aspx?
https://toubiao.alltobid.com/car/gui/bid.aspx?

http://tbquery.alltobid.com/carnetbidinfo.html

https://tbresult2.alltobid.com/car/gui/querybid.aspx?
https://tblogin2.alltobid.com/car/gui/login.aspx?
https://toubiao2.alltobid.com/car/gui/imagecode.aspx?
https://toubiao2.alltobid.com/car/gui/bid.aspx?

http://tbquery2.alltobid.com/carnetbidinfo.html

 ************************************************** */

#endif // SERVER_H_INCLUDED

