
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "proto_checkcode.h"
#include "proto_make.h"

//#ifdef	DEBUGP4
//#undef	DEBUGP4
//#define 	DEBUGP4(templt, args...)
//#endif

unsigned int 	version = 177;

//===================================================================

// GET /car/gui/imagecode.aspx?BIDNUMBER=52219990&BIDPASSWORD=3319&BIDAMOUNT=100&VERSION=177&CHECKCODE=bd7ac068108c675c29de8afa641393e7 HTTP/1.0\r\nContent-Type: text/html\r\nHost: toubiao2.alltobid.com:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; Indy Library)\r\n\r\n

#define IMAGE_AA "GET /car/gui/imagecode.aspx?BIDNUMBER=%.8d&BIDPASSWORD=%.4d&BIDAMOUNT=%d&VERSION=%d&CHECKCODE=%s HTTP/1.0\r\nContent-Type: text/html\r\nHost: toubiao.alltobid.com:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; Indy Library)\r\n\r\n"

#define IMAGE_BB "GET /car/gui/imagecode.aspx?BIDNUMBER=%.8d&BIDPASSWORD=%.4d&BIDAMOUNT=%d&VERSION=%d&CHECKCODE=%s HTTP/1.0\r\nContent-Type: text/html\r\nHost: toubiao2.alltobid.com:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; Indy Library)\r\n\r\n"

// GET /car/gui/imagecode.aspx?BIDNUMBER=52219990&BIDPASSWORD=3319&BIDAMOUNT=100&VERSION=177&CHECKCODE=bd7ac068108c675c29de8afa641393e7 HTTP/1.0\r\nContent-Type: text/html\r\nHost: toubiao2.alltobid.com:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; Indy Library)\r\nCookie: JSESSIONID=B0C0BACB0500C9B5530D6DD7591964BD\r\n\r\n

#define IMAGE_A "GET /car/gui/imagecode.aspx?BIDNUMBER=%.8d&BIDPASSWORD=%.4d&BIDAMOUNT=%d&VERSION=%d&CHECKCODE=%s HTTP/1.0\r\nContent-Type: text/html\r\nHost: toubiao.alltobid.com:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; Indy Library)\r\nCookie: JSESSIONID=%s\r\n\r\n"

#define IMAGE_B "GET /car/gui/imagecode.aspx?BIDNUMBER=%.8d&BIDPASSWORD=%.4d&BIDAMOUNT=%d&VERSION=%d&CHECKCODE=%s HTTP/1.0\r\nContent-Type: text/html\r\nHost: toubiao2.alltobid.com:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; Indy Library)\r\nCookie: JSESSIONID=%s\r\n\r\n"

// GET /car/gui/bid.aspx?BIDNUMBER=52219990&BIDPASSWORD=3319&BIDAMOUNT=100&MACHINECODE=5VM0GAG1&CHECKCODE=01c6d52dc2d7dadb024de3e780ff58f4&VERSION=177&IMAGENUMBER=848493 HTTP/1.0\r\nContent-Type: text/html\r\nHost: toubiao2.alltobid.com:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; Indy Library)\r\nCookie: JSESSIONID=9E547C5BF6FF532C8F0A6093BAF6D7A2\r\n\r\n

#define PRICE_A "GET /car/gui/bid.aspx?BIDNUMBER=%.8d&BIDPASSWORD=%.4d&BIDAMOUNT=%d&MACHINECODE=%s&CHECKCODE=%s&VERSION=%d&IMAGENUMBER=%.6d HTTP/1.0\r\nContent-Type: text/html\r\nHost: toubiao.alltobid.com:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; Indy Library)\r\nCookie: JSESSIONID=%s\r\n\r\n"

#define PRICE_B "GET /car/gui/bid.aspx?BIDNUMBER=%.8d&BIDPASSWORD=%.4d&BIDAMOUNT=%d&MACHINECODE=%s&CHECKCODE=%s&VERSION=%d&IMAGENUMBER=%.6d HTTP/1.0\r\nContent-Type: text/html\r\nHost: toubiao2.alltobid.com:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; Indy Library)\r\nCookie: JSESSIONID=%s\r\n\r\n"

// GET /car/gui/login.aspx?BIDNUMBER=52219990&BIDPASSWORD=3319&MACHINECODE=5VM0GAG1&CHECKCODE=ea21a7115750a224e57532f8abe209b9&VERSION=177&IMAGENUMBER=625233 HTTP/1.0\r\nContent-Type: text/html\r\nHost: tblogin2.alltobid.com:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; IndyLibrary)\r\n\r\n

#define LOGIN_A "GET /car/gui/login.aspx?BIDNUMBER=%.8d&BIDPASSWORD=%.4d&MACHINECODE=%s&CHECKCODE=%s&VERSION=%d&IMAGENUMBER=%.6d HTTP/1.0\r\nContent-Type: text/html\r\nHost: tblogin.alltobid.com:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; IndyLibrary)\r\n\r\n"

#define LOGIN_B "GET /car/gui/login.aspx?BIDNUMBER=%.8d&BIDPASSWORD=%.4d&MACHINECODE=%s&CHECKCODE=%s&VERSION=%d&IMAGENUMBER=%.6d HTTP/1.0\r\nContent-Type: text/html\r\nHost: tblogin2.alltobid.com:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; Indy Library)\r\n\r\n"

//===================================================================

char* proto_makeprice(
		int group,
		unsigned int bidnumber,
		unsigned int bidpassword,
		unsigned int bidamount,
		unsigned int imagenumber,
		char* machinecode,
		char* sessionid,
		char* proto)
{
	char checkcode[33]={0};

	proto_makecode(
			bidnumber,
			bidpassword,
			bidamount,
			imagenumber,
			version,
			machinecode,
			checkcode);

	if(group == 0)
		sprintf(
				proto, 
				PRICE_A,
				bidnumber,
				bidpassword,
				bidamount,
				machinecode,
				checkcode,
				version,
				imagenumber,
				sessionid);
	else
		sprintf(
				proto, 
				PRICE_B,
				bidnumber,
				bidpassword,
				bidamount,
				machinecode,
				checkcode,
				version,
				imagenumber,
				sessionid);

	return proto ;
}


char* proto_makelogin(
		int group,
		unsigned int bidnumber,
		unsigned int bidpassword,
		unsigned int imagenumber,
		char* machinecode,
		char* proto)
{
	char checkcode[33]={0};

	proto_makecode(
			bidnumber,
			bidpassword,
			0,
			imagenumber,
			version,
			machinecode,
			checkcode);

	if(group == 0)
		sprintf(
				proto,
				LOGIN_A,
				bidnumber,
				bidpassword,
				machinecode,
				checkcode,
				version,
				imagenumber);
	else
		sprintf(
				proto,
				LOGIN_B,
				bidnumber,
				bidpassword,
				machinecode,
				checkcode,
				version,
				imagenumber);

	return proto ;
}

char* proto_makeimage(
		int group,
		unsigned int bidnumber,
		unsigned int bidpassword,
		unsigned int bidamount,
		char* sessionid,
		char* proto)
{
	char checkcode[33]={0};

	proto_makeimagecode(
			bidnumber,
			bidpassword,
			bidamount,
			version,
			checkcode);

	if(sessionid[0] == 0) {
		if(group == 0)
			sprintf(
					proto, 
					IMAGE_AA, 
					bidnumber, 
					bidpassword, 
					bidamount, 
					version, 
					checkcode);
		else
			sprintf(
					proto, 
					IMAGE_BB, 
					bidnumber, 
					bidpassword, 
					bidamount, 
					version, 
					checkcode);
	} 
	else {
		if(group == 0)
			sprintf(
					proto, 
					IMAGE_A, 
					bidnumber, 
					bidpassword, 
					bidamount, 
					version, 
					checkcode,
					sessionid);
		else
			sprintf(
					proto, 
					IMAGE_B, 
					bidnumber, 
					bidpassword, 
					bidamount, 
					version, 
					checkcode,
					sessionid);

	}

	return proto ;
}


