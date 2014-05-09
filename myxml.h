
#ifndef MYXML_H_INCLUDED
#define MYXML_H_INCLUDED


#define MAX_DICT	32
#define LEN_KEY		256
#define LEN_VAL		4096

typedef struct{
	char	key[LEN_KEY];
	char	val[LEN_VAL];
} XML_DICT;

int myxml_parseMemory(char* buff, XML_DICT* xml_dict, int* number, int max_number);

int myxml_parseFile(char* filename, XML_DICT* xml_dict, int* number, int max_number);

void myxml_init(void);

void myxml_clean(void);

#endif // MYXML_H_INCLUDED

