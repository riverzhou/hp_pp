
#ifndef PROC_H_INCLUDED
#define PROC_H_INCLUDED

#include <pthread.h>

//#include "user.h"

int proc_login(int user_id, int delay);

int proc_image(int user_id, int bid_id, int delay);

int proc_price(int user_id, int bid_id, int delay);

int proc_decode_connect(void);

int proc_decode(int user_id, int bid_id, int dm_fd);

int proc_login_udp(int user_id, int option);

void proc_status_udp(int user_id, int option);

int proc_logout_udp(int user_id, int option);

void proc_trigger(void);

#endif // PROC_H_INCLUDED

