
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

//#include <errno.h>
//#include <ctype.h>
//#include <openssl/md5.h>


#include "log.h"  
#include "myssl.h"  
#include "myudp.h"  
#include "proto_checkcode.h"  
#include "proto_make.h"  
#include "server.h"

// DEBUGP1

#define SEND_BUFF_SIZE 	4096
#define RECV_BUFF_SIZE  4096

//================================================================

int bidnumber		= 98765432;
int bidpassword		= 4321 ;
int bidamount		= 545400;

int inumber_a		= 667044 ;
int inumber_c		= 928393 ;

int version 		= 177 ;
char machinecode[] 	= "VB8c560dd2-2de8b7c4" ;
char session_b[]   	= "B0C0BACB0500C9B5530D6DD7591964BD" ;
char session_c[]   	= "9E547C5BF6FF532C8F0A6093BAF6D7A2" ;

//-----------------------------------------------------------------

void main_init(void)
{
	log_init();
	server_init();
	myssl_init();
}

void main_close(void)
{
	log_close();
}

int proc_login(
		int		group,
		unsigned int	bidnumber,
		unsigned int	bidpassword,
		unsigned int	imagenumber,
		unsigned int	version,
		char*		machinecode)
{
	int channel_id   =-1 ;
	int server	 =-1 ;	
	char proto[SEND_BUFF_SIZE] ={0};
	char buff[RECV_BUFF_SIZE]  ={0};

	if(group == 0)
		server = LOGIN_A;
	else
		server = LOGIN_B;

	memset(proto, 0, sizeof(proto));
	proto_makelogin(
			group,
			bidnumber,
			bidpassword,
			imagenumber,
			version,
			machinecode,
			proto);

	channel_id = channel_findfree();

	DEBUGP1("conn to LOGIN server... \n");
	if(myssl_connect(channel_id, server) < 0 ){
		myssl_close(channel_id);
		return -1;
	}

	DEBUGP1("send to LOGIN server... \n");

	myssl_datawrite(channel_id, proto, strlen(proto));
	DEBUGP1("%s\n", proto);
	LOGT1("\n");
	LOGP1("%s", proto);
	LOGT1("\n");

	DEBUGP1("recv from LOGIN server... \n");

	int ret = 0;
	do{
		memset(buff, 0, sizeof(buff));
		ret = myssl_dataread(channel_id, buff, sizeof(buff));
		buff[sizeof(buff)-1] = 0;
		DEBUGP1("%s\n", buff);
		LOGT1("\n");
		LOGP1("%s", buff);
		LOGT1("\n");
	} while(ret !=0 );

	myssl_close(channel_id);

	return 0;
}

int proc_image(
		int		group,
		unsigned int	bidnumber,
		unsigned int	bidpassword,
		unsigned int	imagenumber,
		unsigned int	version,
		char*		machinecode)
{
	int channel_id   =-1 ;
	int server	 =-1 ;	
	char proto[SEND_BUFF_SIZE] ={0};
	char buff[RECV_BUFF_SIZE]  ={0};

	if(group == 0)
		server = LOGIN_A;
	else
		server = LOGIN_B;

	memset(proto, 0, sizeof(proto));
	proto_makelogin(
			group,
			bidnumber,
			bidpassword,
			imagenumber,
			version,
			machinecode,
			proto);

	channel_id = channel_findfree();

	DEBUGP1("conn to LOGIN server... \n");
	if(myssl_connect(channel_id, server) < 0 ){
		myssl_close(channel_id);
		return -1;
	}

	DEBUGP1("send to LOGIN server... \n");

	myssl_datawrite(channel_id, proto, strlen(proto));
	DEBUGP1("%s\n", proto);
	LOGT1("\n");
	LOGP1("%s", proto);
	LOGT1("\n");

	DEBUGP1("recv from LOGIN server... \n");

	int ret = 0;
	do{
		memset(buff, 0, sizeof(buff));
		ret = myssl_dataread(channel_id, buff, sizeof(buff));
		buff[sizeof(buff)-1] = 0;
		DEBUGP1("%s\n", buff);
		LOGT1("\n");
		LOGP1("%s", buff);
		LOGT1("\n");
	} while(ret !=0 );

	myssl_close(channel_id);

	return 0;
}


void print_proto(void)
{
	char proto[1024] ={0};	

	printf("---------------------------------------------------------------------\r\n");

	memset(proto, 0, sizeof(proto));
	proto_makelogin(
			0,
			bidnumber,
			bidpassword,
			inumber_a,
			version,
			machinecode,
			proto);
	printf("\r\n\r\n");
	printf("%s\r\n", proto);
	printf("---------------------------------------------------------------------\r\n");

	memset(proto, 0, sizeof(proto));
	proto_makeimage(
			0,
			bidnumber,
			bidpassword,
			bidamount,
			version,
			session_b,
			proto);
	printf("\r\n\r\n");
	printf("%s\r\n", proto);
	printf("---------------------------------------------------------------------\r\n");

	memset(proto, 0, sizeof(proto));
	proto_makeprice(
			0,
			bidnumber,
			bidpassword,
			bidamount,
			inumber_c,
			version,
			machinecode,
			session_c,
			proto);
	printf("\r\n\r\n");
	printf("%s\r\n", proto);
	printf("---------------------------------------------------------------------\r\n");
}

int main(int argc, char** argv)
{
	main_init();

	DEBUGT1("test begin.....\n");
	LOGT1("test begin.....\n");

	//print_proto();

	main_login(
			0,
			bidnumber,
			bidpassword,
			inumber_a,
			version,
			machinecode);


	DEBUGT1("test end.....\n");
	LOGT1("test end.....\n");

	main_close();

	return 0;
}

