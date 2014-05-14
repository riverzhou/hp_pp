
#ifndef LOG_H_INCLUDED
#define LOG_H_INCLUDED

#include <time.h>
#include <sys/time.h>

#ifdef _MINGW_
#define LOG_FILE    		"\\pp.log"
#else
#define LOG_FILE    		"/pp.log"
#endif

#define DEB_FILE 		stderr

//#define FUNC_NAME_HEAD	"%-20s : "
#define FUNC_NAME_HEAD		"%20s : "

//====================================================================================

// 外部接口：DEBUGP1() DEBUGT1()	用法同  printf()

#define DEBUGP1(templt, args...) 
#define DEBUGP2(templt, args...) 
#define DEBUGP3(templt, args...) 
#define DEBUGP4(templt, args...) 
#define DEBUGP5(templt, args...) 

#ifdef _DEBUG1_
#undef 	DEBUGP1
#define DEBUGP1(templt, args...) \
	do {\
		fprintf(DEB_FILE, templt,##args);\
		fflush(DEB_FILE);\
	}while(0)
#endif

#ifdef _DEBUG2_
#undef 	DEBUGP2
#define DEBUGP2(templt, args...) \
	do {\
		fprintf(DEB_FILE, templt,##args);\
		fflush(DEB_FILE);\
	}while(0)
#endif

#ifdef _DEBUG3_
#undef 	DEBUGP3
#define DEBUGP3(templt, args...) \
	do {\
		fprintf(DEB_FILE, templt,##args);\
		fflush(DEB_FILE);\
	}while(0)
#endif

#ifdef _DEBUG4_
#undef 	DEBUGP4
#define DEBUGP4(templt, args...) \
	do {\
		fprintf(DEB_FILE, templt,##args);\
		fflush(DEB_FILE);\
	}while(0)
#endif

#ifdef _DEBUG5_
#undef 	DEBUGP5
#define DEBUGP5(templt, args...) \
	do {\
		fprintf(DEB_FILE, templt,##args);\
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


