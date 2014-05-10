
cc = gcc

rm = rm -f

files = dm_client.c

all:
	$(cc) $(def) $(debug_number) $(log_level) -O2 -Wall -std=gnu99 ${files}  -o  dm_client
	strip dm_client

clean:
	$(rm) dm_client core

