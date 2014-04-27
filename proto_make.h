
#ifndef PROTO_MAKE_H_INCLUDED
#define PROTO_MAKE_H_INCLUDED

char* proto_makelogin(
                int group,
                unsigned int bidnumber,
                unsigned int bidpassword,
                unsigned int imagenumber,
                char* machinecode,
                char* proto);


char* proto_makeprice(
                int group,
                unsigned int bidnumber,
                unsigned int bidpassword,
                unsigned int bidamount,
                unsigned int imagenumber,
                char* machinecode,
		char* sessionid,
                char* proto);

char* proto_makeimage(
                int group,
                unsigned int bidnumber,
                unsigned int bidpassword,
                unsigned int bidamount,
		char* sessionid,
                char* proto);



#endif // PROTO_MAKE_H_INCLUDED



