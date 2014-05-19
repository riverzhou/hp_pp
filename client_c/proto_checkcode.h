
#ifndef PROTO_CHECKCODE_H_INCLUDED
#define PROTO_CHECKCODE_H_INCLUDED

char* proto_makecode(
		unsigned int bidnumber,
		unsigned int bidpassword,
		unsigned int bidamount,
		unsigned int imagenumber,
		unsigned int version,
		char* machinecode,
		char* checkcode);


char* proto_makeimagecode(
		unsigned int bidnumber,
		unsigned int bidpassword,
		unsigned int bidamount,
		unsigned int version,
		char* checkcode);

#endif // PROTO_CHECKCODE_H_INCLUDED

