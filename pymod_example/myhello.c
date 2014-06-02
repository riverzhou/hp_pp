

#include <stdio.h>

#include "myhello.h"

int myhello(int n)
{
	for(int i = 0 ; i < n ; i++) {
		printf("from myhello\n");
	}
	return n;
}	

