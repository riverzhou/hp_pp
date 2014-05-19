
#ifndef UDP_CLIENT_H_INCLUDED
#define UDP_CLIENT_H_INCLUDED

//---------------------------------------------
//
#define MAX_UDP_BUFFLEN   	1500

#define UDP_TIMEOUT		5

//---------------------------------------------
int udp_login(int user_id);

int udp_getinfo(int user_id);

int udp_logout(int user_id);

//---------------------------------------------

#endif // UDP_CLIENT_H_INCLUDED

