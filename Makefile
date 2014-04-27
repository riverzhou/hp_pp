
cc = gcc

rm = rm -f

#debug_number= -D_DEBUG5_ -D_DEBUG4_ -D_DEBUG3_ -D_DEBUG2_ -D_DEBUG1_ 
debug_number= -D_DEBUG2_ -D_DEBUG1_ -D_DEBUG5_

log_level = -D_LOG_LEVEL_=5

files = log.c  myrand.c  myssl.c  myudp.c  myxml.c  pp.c  proc.c  proto_checkcode.c  proto_make.c  proto_parse.c  server.c  user.c

#test_files = 

#def = -D__MINGW__

#xml:
#	$(cc) $(debug_number) $(log_level) -O2 -Wall -std=gnu99 myxml.c -o myxml -I/usr/include/libxml2 -lxml2

all:
	$(cc) $(def) $(debug_number) $(log_level) -O2 -Wall -std=gnu99 ${files} -lssl -lcrypto -pthread -o pp -I/usr/include/libxml2 -lxml2
#	$(cc) $(debug_number) $(log_level) -O2 -Wall -std=gnu99 ${test_files} -lssl -lcrypto -o pp_test
	strip pp

clean:
	$(rm) pp pp.log  pp_test

