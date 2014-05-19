
#ifndef MYRAND_H_INCLUDED
#define MYRAND_H_INCLUDED


void myrand_init(void);

unsigned int myrand_getint(unsigned int max);

unsigned char myrand_getchar(void);

unsigned char myrand_getnum(void);

unsigned char myrand_gethex(void);

unsigned char* myrand_getstr(unsigned char* buff, int len);


#endif // MYRAND_H_INCLUDED

