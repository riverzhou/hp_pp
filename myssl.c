
#ifdef _MINGW_
#include <windows.h>
#else 
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#endif

#include <stdio.h>
#include <stdlib.h>

#include "myssl.h"
#include "server.h"
#include "log.h"

// DEBUGP2
// LOGP3

//==========================================================================

int channel_findfree(void)
{
	int id = -1;

	for(int i = 0 ; i < MAX_CHANNEL ; i++ ) {
		if(channel[i].fd == 0 ){
			id = i ;
			break;
		}

	}
	return id;
}

void ShowCerts(SSL * ssl)
{
	X509 *cert;
	char *line;

	cert = SSL_get_peer_certificate(ssl);
	if (cert != NULL) {
		line = X509_NAME_oneline(X509_get_subject_name(cert), 0, 0);
		DEBUGP2("证书: %s\n", line);
		LOGP3("证书: %s\n", line);
		free(line);
		line = X509_NAME_oneline(X509_get_issuer_name(cert), 0, 0);
		DEBUGP2("颁发者: %s\n", line);
		LOGP3("颁发者: %s\n", line);
		free(line);
		X509_free(cert);
	} else
		DEBUGP2("无证书信息！\n");
}

#ifdef _MINGW_
void net_init(void)
{
	WSADATA wsa;
	WSAStartup(MAKEWORD(2,2), &wsa);
}
#endif

void myssl_init(void)
{
	SSL_library_init();
	OpenSSL_add_all_algorithms();
	SSL_load_error_strings();

	memset(channel, 0, sizeof(channel[MAX_CHANNEL]));
}

int myssl_connect(int channel_id, int server_id)
{
	if(channel_id < 0)
		return -1;

	DEBUGT2("try to connect to %d : %s : %s \n", server_id, server[server_id].domain, inet_ntoa(*(struct in_addr *)(&server[server_id].addr.sin_addr)));
	LOGT3("try to connect to %d : %s : %s \n", server_id, server[server_id].domain, inet_ntoa(*(struct in_addr *)(&server[server_id].addr.sin_addr)));

	channel[channel_id].fd = socket(AF_INET, SOCK_STREAM, 0);
	if ( channel[channel_id].fd < 0 ) {
		perror("Socket");
		return -1;
	}
	if (connect(channel[channel_id].fd, (struct sockaddr *) &(server[server_id].addr), sizeof(struct sockaddr_in)) != 0) {
		perror("Connect ");
		return -1;
	}

	channel[channel_id].ctx = SSL_CTX_new(SSLv23_client_method());
	if ( channel[channel_id].ctx == NULL ) {
		ERR_print_errors_fp(stderr);
		return -1;
	}
	channel[channel_id].ssl = SSL_new(channel[channel_id].ctx);
	SSL_set_fd(channel[channel_id].ssl, channel[channel_id].fd);

	if (SSL_connect(channel[channel_id].ssl) == -1) {
		ERR_print_errors_fp(stderr);
		return -1;
	}
	else {
		DEBUGP2("channel %d connect to %s \n", channel_id, server[server_id].domain);
		DEBUGP2("Connected with %s encryption \n", SSL_get_cipher(channel[channel_id].ssl));
		ShowCerts(channel[channel_id].ssl);
		DEBUGP2("\n");
	}

	return 0;
}
int myssl_close(int channel_id)
{
	if(channel[channel_id].ssl != NULL)
		SSL_shutdown(channel[channel_id].ssl);

	if(channel[channel_id].ssl != NULL)
		SSL_free(channel[channel_id].ssl);

	if(channel[channel_id].fd > 0){
		shutdown(channel[channel_id].fd, SHUT_RDWR);
#ifdef _MINGW_
		closesocket(channel[channel_id].fd);
#else
		close(channel[channel_id].fd);
#endif
	}

	if(channel[channel_id].ctx != NULL)
		SSL_CTX_free(channel[channel_id].ctx);

	memset(&(channel[channel_id]), 0, sizeof(CHANNEL) );

	return 0;
}

int myssl_datawrite(int channel_id, char* buf, int len)
{
	return SSL_write(channel[channel_id].ssl, buf, len);
}

int myssl_dataread(int channel_id, char* buf, int len)
{
	return SSL_read(channel[channel_id].ssl, buf, len);
}



