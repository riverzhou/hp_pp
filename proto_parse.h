
#ifndef PROTO_PARSE_H_INCLUDED
#define PROTO_PARSE_H_INCLUDED

#include "user.h"

int proto_parselogin(
		char*           buff,
		RESULT_LOGIN*   result_login);

int proto_parseimage(
		char*           buff,
		RESULT_IMAGE*   result_image);

int proto_parseprice(
		char*           buff,
		RESULT_PRICE*  	result_price);

#endif  // PROTO_PARSE_H_INCLUDED

