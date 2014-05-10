
cc = gcc

rm = rm -f

files = udp_client.c

all:
	$(cc) $(def) $(debug_number) $(log_level) -O2 -Wall -std=gnu99 ${files}  -o  udp_client
	strip udp_client

clean:
	$(rm) udp_client core

