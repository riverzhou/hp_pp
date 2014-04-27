
#ifndef PROC_H_INCLUDED
#define PROC_H_INCLUDED

#ifdef _MINGW_
#include <windows.h>
#else
#include <pthread.h>
#endif

//#include "user.h"

int proc_login(
		int             group,
		unsigned int    bidnumber,
		unsigned int    bidpassword,
		unsigned int    imagenumber,
		char*           machinecode,
		RESULT_LOGIN*   result_login);

int proc_image(
		int             group,
		unsigned int    bidnumber,
		unsigned int    bidpassword,
		unsigned int*   bidamount,
		char*           sessionid,
		RESULT_IMAGE*   result_image,
		EVENT*          event);

int proc_price(
		int             group,
		unsigned int    bidnumber,
		unsigned int    bidpassword,
		unsigned int*   bidamount,
		unsigned int    imagenumber,
		char*           machinecode,
		char*           sessionid,
		RESULT_PRICE*  	result_price,
		EVENT*          event);

int proc_decode(
		char*           pic,
		unsigned int*   image ,
		EVENT*          event);


#endif // PROC_H_INCLUDED

