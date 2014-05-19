
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "log.h"
#include "proto_parse.h"
#include "myxml.h"

//#ifdef	DEBUGP4
//#undef	DEBUGP4
//#define 	DEBUGP4(templt, args...)
//#endif

//===================================================================

char* proto_parsehtml_getval(char* buff, char* key, char* sym, char* end, char* val, int val_len)
{
	char* p1 = NULL;
	char* p2 = NULL;
	char* p3 = NULL;
	char  s  = 0;

	p1  = strstr(buff, key);
	if(p1 == NULL) {
		DEBUGP4("key no found in buff. proto_parsehtml_getval \n");
		return NULL;
	}

	p2  = strstr(p1, end);
	if(p1 == NULL) {
		DEBUGP4("end no found in buff. proto_parsehtml_getval \n");
		return NULL;
	}
	s   = *p2;
	*p2 = 0;

	p3  = strstr(p1, sym);
	if(p1 == NULL) {
		DEBUGP4("sym no found in buff. proto_parsehtml_getval \n");
		*p2 = s;
		return NULL;
	}
	p3 += strlen(sym);

	DEBUGP4("val: %s\n", p3);
	strncpy(val, p3, val_len - 1); 

	*p2 = s;
	return val;
}

int proto_parselogin_head(
		char* 		buff, 
		RESULT_LOGIN* 	result_login)
{
	char val[128] = {0};

	proto_parsehtml_getval(buff, "JSESSIONID", "=", ";", val, sizeof(val) - 1);
	strncpy(result_login->sid, val, sizeof(result_login->sid) - 1 );

	return 0;
}

int proto_parseimage_head(
		char* 		buff, 
		RESULT_IMAGE* 	result_image)
{
	char val[128] = {0};

	proto_parsehtml_getval(buff, "JSESSIONID", "=", ";", val, sizeof(val) - 1);
	strncpy(result_image->sid, val, sizeof(result_image->sid) - 1);

	return 0;
}

int proto_parseprice_head(
		char* 		buff, 
		RESULT_PRICE* 	result_price)
{
	char val[128] = {0};

	proto_parsehtml_getval(buff, "JSESSIONID", "=", ";", val, sizeof(val) - 1);
	strncpy(result_price->sid, val, sizeof(result_price->sid) - 1);

	return 0;
}

int proto_parselogin_body(
		char*           buff,
		RESULT_LOGIN*   result_login)
{
	int number = 0;
	XML_DICT xml_dict[MAX_XML_DICTLEN];
	memset(xml_dict, 0, sizeof(xml_dict));

	myxml_parseMemory(buff, xml_dict, &number, MAX_XML_DICTLEN - 1);

	for(int i = 0 ; i < number ; i++ ){
		DEBUGP4("%32s = %s \n", xml_dict[i].key, xml_dict[i].val);

		if(strcmp(xml_dict[i].key, "CLIENTNAME") == 0) {
			strncpy(result_login->name, xml_dict[i].val, sizeof(result_login->name) - 1);
			continue;
		}

		if(strcmp(xml_dict[i].key, "PID") == 0) {
			strncpy(result_login->pid, xml_dict[i].val, sizeof(result_login->pid) - 1);
			continue;
		}
	}

	return 0;
}

int proto_parseimage_body(
		char*           buff,
		RESULT_IMAGE*   result_image)
{
	int number = 0;
	XML_DICT xml_dict[MAX_XML_DICTLEN];
	memset(xml_dict, 0, sizeof(xml_dict));

	myxml_parseMemory(buff, xml_dict, &number, MAX_XML_DICTLEN - 1);

	for(int i = 0 ; i < number ; i++ ){
		DEBUGP4("%32s = %s \n", xml_dict[i].key, xml_dict[i].val);

		if(strcmp(xml_dict[i].key, "ERRORCODE") == 0) {
			strncpy(result_image->errcode, xml_dict[i].val, sizeof(result_image->errcode) - 1);
			continue;
		}

		if(strcmp(xml_dict[i].key, "ERRORSTRING") == 0) {
			strncpy(result_image->errstr, xml_dict[i].val, sizeof(result_image->errstr) - 1);
			continue;
		}

		if(strcmp(xml_dict[i].key, "IMAGE_CONTENT") == 0) {
			strncpy(result_image->pic_64, xml_dict[i].val, sizeof(result_image->pic_64) - 1);
			continue;
		}
	}

	return 0;
}

int proto_parseprice_body(
		char*           buff,
		RESULT_PRICE*  	result_price)
{
	int number = 0;
	XML_DICT xml_dict[MAX_XML_DICTLEN];
	memset(xml_dict, 0, sizeof(xml_dict));

	myxml_parseMemory(buff, xml_dict, &number, MAX_XML_DICTLEN - 1);

	for(int i = 0 ; i < number ; i++ ){
		DEBUGP4("%32s = %s \n", xml_dict[i].key, xml_dict[i].val);

		if(strcmp(xml_dict[i].key, "CLIENTNAME") == 0) {
			strncpy(result_price->name, xml_dict[i].val, sizeof(result_price->name) - 1);
			continue;
		}

		if(strcmp(xml_dict[i].key, "PID") == 0) {
			strncpy(result_price->pid, xml_dict[i].val, sizeof(result_price->pid) - 1);
			continue;
		}

		if(strcmp(xml_dict[i].key, "BIDNUMBER") == 0) {
			strncpy(result_price->number, xml_dict[i].val, sizeof(result_price->number) - 1);
			continue;
		}

		if(strcmp(xml_dict[i].key, "BIDCOUNT") == 0) {
			strncpy(result_price->count, xml_dict[i].val, sizeof(result_price->count) - 1);
			continue;
		}

		if(strcmp(xml_dict[i].key, "BIDAMOUNT") == 0) {
			strncpy(result_price->price, xml_dict[i].val, sizeof(result_price->price) - 1);
			continue;
		}

		if(strcmp(xml_dict[i].key, "BIDTIME") == 0) {
			strncpy(result_price->time, xml_dict[i].val, sizeof(result_price->time) - 1);
			continue;
		}
	}

	return 0;
}

// ------------------------------------------

int proto_parselogin(
		char*           buff,
		RESULT_LOGIN*   result_login)
{
	char* xmlhead = NULL;

	xmlhead = strstr(buff, "\r\n\r\n");
	xmlhead[2] = 0;
	xmlhead[3] = 0;
	xmlhead += 4;

	proto_parselogin_head(buff, 	result_login);
	proto_parselogin_body(xmlhead, 	result_login);

	return 0;
}

int proto_parseimage(
		char*           buff,
		RESULT_IMAGE*   result_image)
{
	char* xmlhead = NULL;

	xmlhead = strstr(buff, "\r\n\r\n");
	xmlhead[2] = 0;
	xmlhead[3] = 0;
	xmlhead += 4;

	proto_parseimage_head(buff, 	result_image);
	proto_parseimage_body(xmlhead, 	result_image);

	return 0;
}

int proto_parseprice(
		char*           buff,
		RESULT_PRICE*   result_price)
{
	char* xmlhead = NULL;

	xmlhead = strstr(buff, "\r\n\r\n");
	xmlhead[2] = 0;
	xmlhead[3] = 0;
	xmlhead += 4;

	proto_parseprice_head(buff, 	result_price);
	proto_parseprice_body(xmlhead, 	result_price);

	return 0;
}


