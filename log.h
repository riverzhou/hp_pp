
#ifndef LOG_H_INCLUDED
#define LOG_H_INCLUDED

#include <time.h>
#include <sys/time.h>

#ifdef _MINGW_
#define LOG_FILE    	"\\pp.log"
#else
#define LOG_FILE    	"/pp.log"
#endif

#define DEB_FILE 	stderr

//====================================================================================

// 外部接口：DEBUGP1() DEBUGT1()	用法同  printf()

#define DEBUGP1(templt, args...) 
#define DEBUGP2(templt, args...) 
#define DEBUGP3(templt, args...) 
#define DEBUGP4(templt, args...) 
#define DEBUGP5(templt, args...) 

#define DEBUGT1(templt, args...) 
#define DEBUGT2(templt, args...) 
#define DEBUGT3(templt, args...) 
#define DEBUGT4(templt, args...) 
#define DEBUGT5(templt, args...) 

#ifdef _DEBUG1_
#undef 	DEBUGP1
#undef 	DEBUGT1
#define DEBUGP1(templt, args...) \
	do {\
		fprintf(DEB_FILE, templt,##args);\
		fflush(DEB_FILE);\
	}while(0)
#define DEBUGT1(templt, args...) \
	do {\
		time_t	deb_now;\
		char	deb_time[25] ={0};\
		time(&deb_now);\
		ctime_r(&deb_now, deb_time);\
		deb_time[24] = 0;\
		fprintf(DEB_FILE,"%s ->|"templt,deb_time,##args);\
		fflush(DEB_FILE);\
	}while(0)
#endif

#ifdef _DEBUG2_
#undef 	DEBUGP2
#undef 	DEBUGT2
#define DEBUGP2(templt, args...) \
	do {\
		fprintf(DEB_FILE, templt,##args);\
		fflush(DEB_FILE);\
	}while(0)
#define DEBUGT2(templt, args...) \
	do {\
		time_t	deb_now;\
		char	deb_time[25] ={0};\
		time(&deb_now);\
		ctime_r(&deb_now, deb_time);\
		deb_time[24] = 0;\
		fprintf(DEB_FILE,"%s ->|"templt,deb_time,##args);\
		fflush(DEB_FILE);\
	}while(0)
#endif

#ifdef _DEBUG3_
#undef 	DEBUGP3
#undef 	DEBUGT3
#define DEBUGP3(templt, args...) \
	do {\
		fprintf(DEB_FILE, templt,##args);\
		fflush(DEB_FILE);\
	}while(0)

#define DEBUGT3(templt, args...) \
	do {\
		time_t	deb_now;\
		char	deb_time[25] ={0};\
		time(&deb_now);\
		ctime_r(&deb_now, deb_time);\
		deb_time[24] = 0;\
		fprintf(DEB_FILE,"%s ->|"templt,deb_time,##args);\
		fflush(DEB_FILE);\
	}while(0)
#endif

#ifdef _DEBUG4_
#undef 	DEBUGP4
#undef 	DEBUGT4
#define DEBUGP4(templt, args...) \
	do {\
		fprintf(DEB_FILE, templt,##args);\
		fflush(DEB_FILE);\
	}while(0)
#define DEBUGT4(templt, args...) \
	do {\
		time_t	deb_now;\
		char	deb_time[25] ={0};\
		time(&deb_now);\
		ctime_r(&deb_now, deb_time);\
		deb_time[24] = 0;\
		fprintf(DEB_FILE,"%s ->|"templt,deb_time,##args);\
		fflush(DEB_FILE);\
	}while(0)
#endif

#ifdef _DEBUG5_
#undef 	DEBUGP5
#undef 	DEBUGT5
#define DEBUGP5(templt, args...) \
	do {\
		fprintf(DEB_FILE, templt,##args);\
		fflush(DEB_FILE);\
	}while(0)
#define DEBUGT5(templt, args...) \
	do {\
		time_t	deb_now;\
		char	deb_time[25] ={0};\
		time(&deb_now);\
		ctime_r(&deb_now, deb_time);\
		deb_time[24] = 0;\
		fprintf(DEB_FILE,"%s ->|"templt,deb_time,##args);\
		fflush(DEB_FILE);\
	}while(0)
#endif

//====================================================================================

// 外部接口：LOG1() LOGT1()	用法同  printf()

#define LOG_SIZE 4096

#define LOGP1(templt, args...) \
	do {\
		char buf[LOG_SIZE+1] ={0};\
		sprintf(buf, templt,##args);\
		buf[LOG_SIZE] = 0;\
		log_write(1, buf);\
	}while(0)

#define LOGT1(templt, args...) \
	do {\
		char buf[LOG_SIZE+1] ={0};\
		sprintf(buf, templt,##args);\
		buf[LOG_SIZE] = 0;\
		log_timewrite(1, buf);\
	}while(0)

#define LOGP2(templt, args...) \
	do {\
		char buf[LOG_SIZE+1] ={0};\
		sprintf(buf, templt,##args);\
		buf[LOG_SIZE] = 0;\
		log_write(2, buf);\
	}while(0)

#define LOGT2(templt, args...) \
	do {\
		char buf[LOG_SIZE+1] ={0};\
		sprintf(buf, templt,##args);\
		buf[LOG_SIZE] = 0;\
		log_timewrite(2, buf);\
	}while(0)


#define LOGP3(templt, args...) \
	do {\
		char buf[LOG_SIZE+1] ={0};\
		sprintf(buf, templt,##args);\
		buf[LOG_SIZE] = 0;\
		log_write(3, buf);\
	}while(0)

#define LOGT3(templt, args...) \
	do {\
		char buf[LOG_SIZE+1] ={0};\
		sprintf(buf, templt,##args);\
		buf[LOG_SIZE] = 0;\
		log_timewrite(3, buf);\
	}while(0)


#define LOGP4(templt, args...) \
	do {\
		char buf[LOG_SIZE+1] ={0};\
		sprintf(buf, templt,##args);\
		buf[LOG_SIZE] = 0;\
		log_write(3, buf);\
	}while(0)

#define LOGT4(templt, args...) \
	do {\
		char buf[LOG_SIZE+1] ={0};\
		sprintf(buf, templt,##args);\
		buf[LOG_SIZE] = 0;\
		log_timewrite(4, buf);\
	}while(0)


#define LOGP5(templt, args...) \
	do {\
		char buf[LOG_SIZE+1] ={0};\
		sprintf(buf, templt,##args);\
		buf[LOG_SIZE] = 0;\
		log_write(5, buf);\
	}while(0)

#define LOGT5(templt, args...) \
	do {\
		char buf[LOG_SIZE+1] ={0};\
		sprintf(buf, templt,##args);\
		buf[LOG_SIZE] = 0;\
		log_timewrite(5, buf);\
	}while(0)

//====================================================================================

void log_init(void);

void log_write(int level, char* buf);

void log_timewrite(int level, char* buf);

void log_close(void);


#endif // LOG_H_INCLUDED


