
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <string.h>

#include "myevent.h"

void myevent_init(EVENT *ev) 
{
	if(ev == NULL)	return;

	ev->signal = 0;
	pthread_mutex_init(&(ev->mutex), NULL);
	pthread_cond_init(&(ev->cond),   NULL);
}

void myevent_clean(EVENT *ev) 
{
	if(ev == NULL)	return;

	pthread_mutex_destroy(&(ev->mutex));
	pthread_cond_destroy(&(ev->cond));
}

int myevent_wait(EVENT *ev)
{
	if(ev == NULL)	return -1;

	int ret = -1;

	pthread_mutex_lock(&(ev->mutex)); 
	while(ev->signal == 0) {
		ret = pthread_cond_wait(&(ev->cond), &(ev->mutex)); 
	}
	pthread_mutex_unlock(&(ev->mutex)); 

	return ret;
}

int myevent_set(EVENT *ev)
{
	if(ev == NULL)	return -1;

	pthread_mutex_lock(&(ev->mutex));
	ev->signal = 1;
	pthread_cond_broadcast(&(ev->cond));
	pthread_mutex_unlock(&(ev->mutex));

	return 0;
}

int myevent_reset(EVENT *ev)
{
	if(ev == NULL)	return -1;

	pthread_mutex_lock(&(ev->mutex));
	ev->signal = 0;
	pthread_mutex_unlock(&(ev->mutex));

	return 0;
}


