
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
//#include <sys/types.h>
//#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

#include "myssl.h"
#include "myrand.h"

#define RAND_DEV        "/dev/urandom"
#define MAX_SEEDLEN	128

char* myrand_get_devseed(char* seed, int seed_len)
{
	int fd  = 0;
	int ret =-1;

	char buff[MAX_SEEDLEN] ={0};

	fd = open(RAND_DEV, O_RDONLY);
	if(fd < 0) {
		perror("open RAND_DEV");
		return NULL;
	}

	ret = read(fd, buff, 64);
	if(ret < 0) {
		perror("read RAND_DEV");
		close(fd);
		return NULL;
	}

	memcpy(seed, buff, 64 );

	close(fd);
	return seed;
}

char* myrand_get_timeseed(char* seed)
{
	unsigned int val ={0};

	val = (int)time(NULL);

	memcpy(seed, &val, 4);

	return seed;
}

void myrand_init(void)
{
	char seed[MAX_SEEDLEN] ={0};

	if(myrand_get_devseed(seed, MAX_SEEDLEN - 1) != NULL){
		RAND_seed(seed, MAX_SEEDLEN - 1);
		return ;
	}

	RAND_seed(myrand_get_timeseed(seed), 4);	
}

// ----------------------------------------------------------------

unsigned int myrand_getint(unsigned int max)
{
	unsigned int val = 0;
	unsigned char buf[5] ={0};

	RAND_bytes(buf, 4);
	memcpy(&val, buf, 4);

	if(val != 0)
		val = val % (max + 1);

	return val;
}

unsigned char myrand_getchar(void)
{
	char abc[] = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" ;
	return abc[myrand_getint(sizeof(abc) - 2)];
}

unsigned char myrand_getnum(void)
{
	char abc[] = "0123456789" ;
	return abc[myrand_getint(sizeof(abc) - 2)];
}

unsigned char myrand_gethex(void)
{
	char abc[] = "0123456789abcdef" ;
	return abc[myrand_getint(sizeof(abc) - 2)];
}

unsigned char* myrand_getstr(unsigned char* buff, int len)
{
	for(int i = 0; i < len - 1; i++){
		buff[i] = myrand_getchar();
	}
	buff[len - 1] = 0;

	return buff;
}


