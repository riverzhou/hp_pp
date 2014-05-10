
#ifndef MYEVENT_H_INCLUDED
#define MYEVENT_H_INCLUDED

#include <pthread.h>

typedef struct {
	int signal;
	pthread_mutex_t mutex;
	pthread_cond_t cond;

} EVENT;

void myevent_init(EVENT *ev);

void myevent_clean(EVENT *ev);

int myevent_wait(EVENT *ev);

int myevent_set(EVENT *ev);

int myevent_reset(EVENT *ev);


#endif // MYEVENT_H_INCLUDED

