
#ifdef _MINGW_
#include <windows.h>
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <string.h>
#endif

#include <stdio.h>
#include <stdlib.h>

#include "server.h"
#include "log.h"

// DEBUGP1

// ====================================================================

void server_init(void)
{
	memset(server, 0, sizeof(server[MAX_SERVER]));

	strcpy(server[LOGIN_A].domain, 		LOGIN_SERVER_A);
	strcpy(server[TOUBIAO_A].domain, 	TOUBIAO_SERVER_A);
	strcpy(server[RESULT_A].domain, 	RESULT_SERVER_A);
	strcpy(server[QUERY_A].domain, 		QUERY_SERVER_A);
	strcpy(server[UDP_A].domain, 		UDP_SERVER_A);

	strcpy(server[LOGIN_B].domain, 		LOGIN_SERVER_B);
	strcpy(server[TOUBIAO_B].domain, 	TOUBIAO_SERVER_B);
	strcpy(server[RESULT_B].domain, 	RESULT_SERVER_B);
	strcpy(server[QUERY_B].domain, 		QUERY_SERVER_B);
	strcpy(server[UDP_B].domain, 		UDP_SERVER_B);

	server[LOGIN_A].port 	= LOGIN_PORT ;
	server[TOUBIAO_A].port 	= TOUBIAO_PORT ;
	server[RESULT_A].port 	= RESULT_PORT ;
	server[QUERY_A].port 	= QUERY_PORT ;
	server[UDP_A].port 	= UDP_PORT ;

	server[LOGIN_B].port 	= LOGIN_PORT ;
	server[TOUBIAO_B].port 	= TOUBIAO_PORT ;
	server[RESULT_B].port 	= RESULT_PORT ;
	server[QUERY_B].port 	= QUERY_PORT ;
	server[UDP_B].port 	= UDP_PORT ;

	for(int i = 0 ; i < MAX_SERVER ; i++) {
		if(server[i].domain[0] != 0 ) {
			struct hostent *host = gethostbyname(server[i].domain);
			if(host != NULL) {
				memcpy(&server[i].addr.sin_addr, host->h_addr_list[0], sizeof(server[i].addr.sin_addr)) ;
				server[i].addr.sin_family = AF_INET;
				server[i].addr.sin_port = htons(server[i].port);
				DEBUGP1("%d :\t %24s : %.6d : %16s \n", i, server[i].domain, server[i].port, inet_ntoa(server[i].addr.sin_addr));
			}
			else{
#ifdef _MINGW_
				LPVOID lpMsgBuf;
				FormatMessage(
						FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM,
						NULL,
						WSAGetLastError(),
						MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
						(LPTSTR) &lpMsgBuf,
						0,
						NULL );
				MessageBox( NULL, (LPCTSTR)lpMsgBuf, "Error", MB_OK | MB_ICONINFORMATION );
				LocalFree( lpMsgBuf );
#else
				perror("gethostbyname");
#endif
			}
		}
	}
}


