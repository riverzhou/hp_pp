
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <ctype.h>

#include "myssl.h"
#include "proto_checkcode.h"
#include "log.h"

//#ifdef	DEBUGP3
//#undef 	DEBUGP3
//#define 	DEBUGP3(templt, args...)
//#endif

//-------------------------------------------------

char* get_md5string(
		char* input, 
		char* output)
{
	unsigned char md[17] = {0};

	if(input == NULL)
		return NULL;

	MD5_CTX ctx;
	MD5_Init(&ctx);
	MD5_Update(&ctx, input, strlen(input));
	MD5_Final(md,&ctx);

	for( int i = 0 ; i < 16 ; i++ ){
		char tmp[3] = {0};
		sprintf(tmp,"%02x",md[i]);
		strcat(output,tmp);
	}

	output[32] = 0;

	return output;
}

//-------------------------------------------------

int proto_bidcode(
		unsigned int bidnumber,
		unsigned int bidpassword,
		unsigned int bidamount)
{
	unsigned int code = 0;

	if( bidnumber == 0 || bidpassword == 0 )
		return 0 ;

	code = bidnumber - bidpassword + bidamount;
	code = code >> 4;

	if(code == 1000)
		code += 1000;

	return code;
}

//从32位MD5码中取出8位
char* proto_bidmd(
		char* input, 
		char* output)
{
	int p[8] = {3,5,11,13,19,21,27,29};

	for(int i = 0 ; i < 8 ; i++) {
		output[i] = input[p[i]-1];	// C的字符串，下标号要-1
	}

	output[8] = 0 ;
	return output;
}

char* proto_makecode(
		unsigned int bidnumber,
		unsigned int bidpassword,
		unsigned int bidamount,
		unsigned int imagenumber,
		unsigned int version,
		char* machinecode,
		char* checkcode)
{
	char endstring[] = "AAA";	// 用于串尾的 magic number
	char md[33] = {0};		// 字符串形式的md5码，128位，16个8进制数，32位字符串

	int  bidcode 	= 0 ;		// 由bidnumber和bidpassword计算和bidamount
	char bid[22] 	={0};		// 32位数字打印10进制最多20位
	char bidmd[9] 	={0};		// 8位数字码(16进)

	char buff[1024] ={0};

	bidcode = proto_bidcode(bidnumber, bidpassword, bidamount) ;

	if( bidcode  == 0 )
		return NULL;

	sprintf(bid, "%d", bidcode);

	DEBUGP3("%s\n", bid);

	if(get_md5string(bid, md) == NULL)
		return NULL;	

	proto_bidmd(md, bidmd);

	DEBUGP3("%s\n", md);

	DEBUGP3("%s\n", bidmd);

	//177（版本号） 1300f299（8位计算码，由账号+密码计算得到） xxxxxx（6位图形验证码）"硬件特征码" AAA（固定字符串）
	sprintf(buff, "%d%s%.6d%s%s", version, bidmd, imagenumber, machinecode, endstring);

	DEBUGP3("%s\n", buff);

	if(get_md5string(buff, checkcode) == NULL)
		return NULL;	

	DEBUGP3("%s\n", checkcode);

	return checkcode;
}


char* proto_makeimagecode(
		unsigned int bidnumber,
		unsigned int bidpassword,
		unsigned int bidamount,
		unsigned int version,
		char* checkcode)
{

	int number = bidnumber - bidamount ;
	char buff[33] ={0} ;

	sprintf(buff, "%d#%d@%.4d", number, version, bidpassword);

	DEBUGP3("%s\n", buff);

	if(get_md5string(buff, checkcode) == NULL)
		return NULL;

	DEBUGP3("%s\n", checkcode);

	return checkcode;
}


