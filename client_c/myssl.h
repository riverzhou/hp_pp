
#ifndef MYSSL_H_INCLUDED
#define MYSSL_H_INCLUDED
//-----------------------------------------------------------------------
#if __APPLE__
#include <AvailabilityMacros.h>
/* Apple has deprecated OpenSSL so it is all warnings - we
   just get rid of those */
#ifdef  DEPRECATED_IN_MAC_OS_X_VERSION_10_7_AND_LATER
#undef  DEPRECATED_IN_MAC_OS_X_VERSION_10_7_AND_LATER
#define DEPRECATED_IN_MAC_OS_X_VERSION_10_7_AND_LATER
#endif
#endif

#include <openssl/err.h>
#include <openssl/evp.h>
#include <openssl/rsa.h>
#include <openssl/sha.h>
#include <openssl/md5.h>
#include <openssl/x509.h>
#include <openssl/rand.h>
#include <openssl/ssl.h>
#include <openssl/crypto.h>

#if __APPLE__
#if defined MAC_OS_X_VERSION_10_7 && MAC_OS_X_VERSION_MIN_REQUIRED >= 1070
/* use accelerated crypto on OS X instead of OpenSSL crypto */
#include <CommonCrypto/CommonDigest.h>
#undef SHA1
#define SHA1 CC_SHA1
#undef MD5
#define MD5 CC_MD5
#endif
#endif
//-----------------------------------------------------------------------

#include "user.h"

#define MAX_CHANNEL	MAX_USER*8 + 20 

typedef struct{
	int flag_use;
	int fd;
	SSL_CTX *ctx;
	SSL *ssl;
}CHANNEL ;

CHANNEL channel[MAX_CHANNEL];

void myssl_init(void);
void myssl_clean(void);

int myssl_connect(int channel_id, int server_id);
int myssl_close(int channel_id);

int myssl_datawrite(int channel_id, char* buf, int len);
int myssl_dataread(int channel_id, char* buf, int len);

int channel_findfree(void);

char* get_md5string(char* output, char* intput);
char* get_md5string_up(char* output, char* input);

#endif // MYSSL_H_INCLUDED

