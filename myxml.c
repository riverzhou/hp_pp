
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <libxml/tree.h>
#include <libxml/parser.h>

#include "log.h"
#include "myxml.h"

void myxml_parseNode(xmlNode* node, xmlDoc* doc, XML_DICT* xml_dict, int* number, int max_number)
{
	if(node == NULL || doc == NULL || xml_dict == NULL || *number >= max_number)
		return ;

	xmlNode *cur_node = NULL;

	for (cur_node = node; cur_node; cur_node = cur_node->next) {
		strncpy(xml_dict[*number].key, (char*)cur_node->name, sizeof(xml_dict[*number].key) - 1);

		xmlChar* xml_val = xmlNodeListGetString(doc, cur_node->xmlChildrenNode, 1);
		if(xml_val != NULL) {
			strncpy(xml_dict[*number].val, (char*)xml_val, sizeof(xml_dict[*number].val) - 1);
			xmlFree(xml_val);
		}

		(*number)++ ;

		myxml_parseNode(cur_node->children, doc, xml_dict, number, max_number);
	}
}

int myxml_parseMemory(char* buff, XML_DICT* xml_dict, int* number, int max_number)
{
	if(buff == NULL || buff[0] == 0)
		return -1;

	xmlDoc* doc	= NULL;
	xmlNode* root 	= NULL;

	doc = xmlParseMemory(buff, strlen(buff));
	if(doc == NULL)
		return -1;

	root = xmlDocGetRootElement(doc);
	if(root == NULL) {	
		xmlFreeDoc(doc);
		xmlCleanupParser();
		return -1;
	}

	*number = 0;
	myxml_parseNode(root, doc, xml_dict, number, max_number);

	xmlFreeDoc(doc);
	xmlCleanupParser(); 

	return 0;
}

int myxml_parseFile(char* filename, XML_DICT* xml_dict, int* number, int max_number)
{
	if(filename == NULL)
		return -1;

	xmlDoc* doc	= NULL;
	xmlNode* root	= NULL;

	doc = xmlParseFile(filename);
	if(doc == NULL)
		return -1;

	root = xmlDocGetRootElement(doc);
	if(root == NULL) {	
		xmlFreeDoc(doc);
		xmlCleanupParser();
		return -1;
	}

	*number = 0;
	myxml_parseNode(root, doc, xml_dict, number, max_number);

	xmlFreeDoc(doc);
	xmlCleanupParser(); 

	return 0;
}



