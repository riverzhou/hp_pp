
#ifndef PPTHREAD_H_INCLUDED
#define PPTHREAD_H_INCLUDED

#include <pthread.h>

#include "myevent.h"

typedef struct {
        int  user_id;
        EVENT* event;
} ARG_THREAD;

void *ppthread_trigger(void* arg_thread);

void *ppthread_client(void* arg_thread);

#endif // PPTHREAD_H_INCLUDED

