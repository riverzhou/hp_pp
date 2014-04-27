
#ifdef _MINGW_
#include <windows.h>
#else
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include <string.h>
#endif

#include "log.h"

// ===================================================================

int	log_level   = 0;
FILE* 	log_LogFile = NULL ;

void log_init(void)
{
	char filename[4096] = {0};
	char* cwd = NULL;

	cwd = getcwd(filename, sizeof(filename) - sizeof(LOG_FILE) - 1);
	if(cwd == NULL){
		perror("getcwd");
		log_level = 0;
		return ;
	}
	strcat(filename, LOG_FILE);

	log_LogFile = fopen(filename, "a") ;
	if(log_LogFile 	== NULL) {
		perror("fopen");
		log_level = 0;
		return ;
	}

#ifdef _LOG_LEVEL_
	log_level  = _LOG_LEVEL_ ;
#else
	log_level  = 5;
#endif
}

#ifndef _MINGW_
typedef struct _SYSTEMTIME {
	unsigned int wYear;
	unsigned int wMonth;
	unsigned int wDayOfWeek;
	unsigned int wDay;
	unsigned int wHour;
	unsigned int wMinute;
	unsigned int wSecond;
	unsigned int wMilliseconds;
} SYSTEMTIME, *PSYSTEMTIME;

void GetLocalTime(SYSTEMTIME* lpSystemTime)
{
	struct timeval 	tv;
	struct tm 	tm_now;

	gettimeofday(&tv , NULL);

	localtime_r(&tv.tv_sec, &tm_now);

	lpSystemTime->wYear 		= tm_now.tm_year+1900;        	//年份
	lpSystemTime->wMonth 		= tm_now.tm_mon+1;            	//月 tm[0-11] sys[1-12]
	lpSystemTime->wDay 		= tm_now.tm_mday;             	//日
	lpSystemTime->wDayOfWeek 	= (tm_now.tm_wday+1)%7 ;       	//tm一星期的日数，从星期一算起，范围为0-6 sys从星期日算起
	lpSystemTime->wHour 		= tm_now.tm_hour;             	//小时
	lpSystemTime->wMinute 		= tm_now.tm_min;               	//分钟
	lpSystemTime->wSecond 		= tm_now.tm_sec;               	//秒

	//lpSystemTime->wMilliseconds 	= tv.tv_usec/1000;           	//毫秒
	lpSystemTime->wMilliseconds 	= tv.tv_usec;           	//微秒,提高精度
}
#endif

char* log_GetLocalTime(char* mytime)
{
	SYSTEMTIME sys;
	GetLocalTime(&sys);
	sprintf(
			mytime, 
#ifdef _MINGW_
			"%4d/%02d/%02d %02d:%02d:%02d.%03d", 
#else
			"%4d/%02d/%02d %02d:%02d:%02d.%06d", 
#endif
			sys.wYear, 
			sys.wMonth, 
			sys.wDay, 
			sys.wHour, 
			sys.wMinute, 
			sys.wSecond, 
			sys.wMilliseconds);
	return mytime;
}

void log_write(int level, char* buf)
{
	if(level > log_level || log_LogFile == NULL )		
		return ;
	fprintf(log_LogFile, "%s", buf);
	fflush(log_LogFile);
}

void log_timewrite(int level, char* buf)
{
	char mytime[40]	= {0};
	if(level > log_level || log_LogFile == NULL )		
		return ;
	fprintf(log_LogFile, "%s ->|%s", log_GetLocalTime(mytime), buf);
	fflush(log_LogFile);
}

void log_close(void)
{
	if(log_LogFile == NULL)	
		return ;
	fclose(log_LogFile);
	log_level = 0;
}

