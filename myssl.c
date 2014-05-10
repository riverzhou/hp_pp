
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

#include <stdio.h>
#include <stdlib.h>

#include <pthread.h>

#include "myssl.h"
#include "server.h"
#include "log.h"

// DEBUGP2
// LOGP5

//==========================================================================

static pthread_mutex_t 	channel_mutex ;

static pthread_mutex_t*	ssl_lock = NULL;

//==========================================================================

void locking_function(int mode, int type, char *file, int line)
{
	// 根据第1个参数mode来判断是加锁还是解锁
	// 第2个参数是数组下标
	if(mode & CRYPTO_LOCK) {
		pthread_mutex_lock(&(ssl_lock[type]));
	}
	else{
		pthread_mutex_unlock(&(ssl_lock[type]));
	}
}

unsigned long id_function(void)
{
	return 	(unsigned long)pthread_self();
}

int ssl_lock_create(void)
{
	// 申请空间，锁的个数是：CRYPTO_num_locks()，
	ssl_lock = OPENSSL_malloc(CRYPTO_num_locks() * sizeof(pthread_mutex_t));
	if(!ssl_lock) {
		return -1;
	}

	for(int i = 0 ; i < CRYPTO_num_locks(); i++){
		pthread_mutex_init(&(ssl_lock[i]), NULL);
	}

	// 设置回调函数，获取当前线程id
	CRYPTO_set_id_callback((unsigned long (*)())id_function);

	// 设置回调函数，加锁和解锁
	CRYPTO_set_locking_callback((void (*)())locking_function);

	return 0;
}

void ssl_lock_cleanup(void)
{
	if(!ssl_lock){
		return;
	}

	CRYPTO_set_locking_callback(NULL);
	for(int i = 0; i < CRYPTO_num_locks(); i++){
		pthread_mutex_destroy(&(ssl_lock[i]));
	}
	OPENSSL_free(ssl_lock);
	ssl_lock = NULL;
}

//==========================================================================

int channel_findfree(void)
{
	int id =-1;

	pthread_mutex_lock(&channel_mutex);
	for(int i = 0 ; i < MAX_CHANNEL ; i++ ) {
		if(channel[i].flag_use == 0 ){
			channel[i].flag_use = 1;
			id = i ;
			break;
		}
	}
	pthread_mutex_unlock(&channel_mutex);

	if(id == -1) {
		DEBUGP2("no free ssl channel \n");
		LOGT1("no free ssl channel \n");
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
		LOGP5("证书: %s\n", line);
		free(line);
		line = X509_NAME_oneline(X509_get_issuer_name(cert), 0, 0);
		DEBUGP2("颁发者: %s\n", line);
		LOGP5("颁发者: %s\n", line);
		free(line);
		X509_free(cert);
	} else
		DEBUGP2("无证书信息！\n");
}

void myssl_init(void)
{
	SSL_library_init();
	OpenSSL_add_all_algorithms();
	SSL_load_error_strings();

	if(ssl_lock_create()){
		DEBUGP2("create ssl lock buffer err: %m\n");
		LOGT5("create ssl lock buffer err: %m\n");
	}

	pthread_mutex_init(&channel_mutex, NULL);

	pthread_mutex_lock(&channel_mutex);
	memset(channel, 0, sizeof(channel[MAX_CHANNEL]));
	pthread_mutex_unlock(&channel_mutex);
}

void myssl_clean(void)
{
	ssl_lock_cleanup();
	pthread_mutex_destroy(&channel_mutex);
}

int myssl_connect(int channel_id, int server_id)
{
	if(channel_id < 0)
		return -1;

	int retry = 3;
	int err   = 0;

	DEBUGP2("try to connect to %d : %s : %s \n", server_id, server[server_id].domain, inet_ntoa(*(struct in_addr *)(&server[server_id].addr.sin_addr)));
	LOGT5("try to connect to %d : %s : %s \n", server_id, server[server_id].domain, inet_ntoa(*(struct in_addr *)(&server[server_id].addr.sin_addr)));

	channel[channel_id].fd = socket(AF_INET, SOCK_STREAM, 0);
	if ( channel[channel_id].fd < 0 ) {
		perror("Socket");
		return -1;
	}

	do{
		err = connect(channel[channel_id].fd, (struct sockaddr *) &(server[server_id].addr), sizeof(struct sockaddr_in));
		if( err != 0) {
			perror("Connect ");
		}
		retry--;
	}while(err != 0 && retry > 0);

	if(err != 0) {
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
		close(channel[channel_id].fd);
	}

	if(channel[channel_id].ctx != NULL)
		SSL_CTX_free(channel[channel_id].ctx);

	pthread_mutex_lock(&channel_mutex);
	memset(&(channel[channel_id]), 0, sizeof(CHANNEL) );
	pthread_mutex_unlock(&channel_mutex);

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



