
cc = gcc

rm = rm -f

#debug_number	= -D_DEBUG5_ -D_DEBUG4_ -D_DEBUG3_ -D_DEBUG2_ -D_DEBUG1_ 
#debug_number	= -D_DEBUG2_ -D_DEBUG5_
debug_number	= -D_DEBUG1_

log_level 	= -D_LOG_LEVEL_=2

files 		= dm_client.c  log.c  myevent.c  myrand.c  myssl.c  myxml.c  pp.c  ppthread.c  proc.c  proto_checkcode.c  proto_make.c  proto_parse.c  server.c  udp_client.c  user.c

all:
	$(cc) $(def) $(debug_number) $(log_level) -O2 -Wall -std=gnu99 ${files} -lxml2 -lssl -lcrypto -pthread -I/usr/include/libxml2 -o pp
	strip pp

clean:
	$(rm) pp pp.log core

