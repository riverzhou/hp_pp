
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include <libxml/tree.h>
#include <libxml/parser.h>

#include "myrand.h"
#include "user.h"
#include "log.h"

#define PRICE0		100
#define PRICE1		74100
#define PRICE2		74200

//---------------------------------------------------------

volatile unsigned int 	flag_login_quit 	= 0;					// login线程退出信号
volatile unsigned int 	flag_trigger_quit 	= 0;					// trigger线程退出信号

volatile unsigned int 	user_amount 		= 0;					// 用户数，从xml配置文件中统计得到

volatile unsigned int 	user_price0 		= PRICE0 ;				// 上半场的投标价格
volatile unsigned int 	user_price1 		= PRICE1 ;				// 下半场的策略1的投标价格
volatile unsigned int 	user_price2 		= PRICE2 ;				// 下半场的策略2的投标价格

EVENT			_ev_login_start;
EVENT			_ev_first_begin;
EVENT			_ev_second_begin;
EVENT			_ev_second_end;
EVENT			_ev_bid0_image_shoot;
EVENT			_ev_bid1_image_shoot;
EVENT			_ev_bid1_image_warmup;
EVENT			_ev_bid1_price_warmup;
EVENT			_ev_bid2_image_shoot;
EVENT			_ev_bid2_image_warmup;
EVENT			_ev_bid2_price_warmup;

EVENT*			ev_login_start   	= &_ev_login_start;			// 开始登录
EVENT*			ev_first_begin   	= &_ev_first_begin;			// 上半场开始
EVENT*			ev_second_begin  	= &_ev_second_begin;			// 下半场开始
EVENT*			ev_second_end    	= &_ev_second_end;			// 全场结束
EVENT*			ev_bid0_image_shoot    	= &_ev_bid0_image_shoot;		// 上半场出价
EVENT*			ev_bid1_image_shoot    	= &_ev_bid1_image_shoot;		// 下半场策略1出价
EVENT*			ev_bid1_image_warmup   	= &_ev_bid1_image_warmup;		// 下半场策略1预热
EVENT*			ev_bid1_price_warmup   	= &_ev_bid1_price_warmup;		// 下半场策略1预热
EVENT*			ev_bid2_image_shoot    	= &_ev_bid2_image_shoot;		// 下半场策略2出价
EVENT*			ev_bid2_image_warmup   	= &_ev_bid2_image_warmup;		// 下半场策略2预热
EVENT*			ev_bid2_price_warmup   	= &_ev_bid2_price_warmup;		// 下半场策略2预热

PP_USER 		pp_user[MAX_USER];

//------------------------------------------------------------------------------------------------

static USER_DICT 	user_dict[MAX_USER];

//-----------------------------------------------------------------------------------------------------------------------------------------------

void user_parseNode(xmlNode* node, xmlDoc* doc, USER_DICT* user_dict, int* number, int max_number)
{
	if(node == NULL || doc == NULL || user_dict == NULL || *number >= max_number)
		return ;

	xmlNode *cur_node = NULL;

	for (cur_node = node; cur_node; cur_node = cur_node->next) {
		if(strcmp((char*)cur_node->name, "user") == 0) {								// 找到账户块
			xmlNode *child_node = cur_node->children;								// 进入账户块
			if(child_node != NULL) {
				for (xmlNode* search_node = child_node; search_node; search_node = search_node->next) {		// 循环遍历账户块内容
					if(strcmp((char*)search_node->name, "number") == 0) {
						xmlChar* xml_val = xmlNodeListGetString(doc, search_node->xmlChildrenNode, 1);
						if(xml_val != NULL) {
							strncpy(user_dict[*number].number, (char*)xml_val, sizeof(user_dict[*number].number) - 1);
							xmlFree(xml_val);
						}
					}
					if(strcmp((char*)search_node->name, "pass") == 0) {
						xmlChar* xml_val = xmlNodeListGetString(doc, search_node->xmlChildrenNode, 1);
						if(xml_val != NULL) {
							strncpy(user_dict[*number].pass, (char*)xml_val, sizeof(user_dict[*number].pass) - 1);
							xmlFree(xml_val);
						}
					}
				}
			}
			(*number)++ ;
			continue;
		}
		user_parseNode(cur_node->children, doc, user_dict, number, max_number);
	}
}

int user_parseFile(char* filename, USER_DICT* user_dict, int* number, int max_number)
{
	if(filename == NULL)
		return -1;

	xmlDoc* doc     = NULL;
	xmlNode* root   = NULL;

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
	user_parseNode(root, doc, user_dict, number, max_number);

	xmlFreeDoc(doc);
	xmlCleanupParser();

	return 0;
}

int user_readconf(void)
{
	char  	filename[4096] 	={0};
	char* 	cwd  		= NULL;
	int 	number 		= 0;

	memset(&user_dict, 0, sizeof(user_dict));

	cwd = getcwd(filename, sizeof(filename) - sizeof(USER_FILE) - 1);
	if(cwd == NULL){
		perror("user conf: getcwd");
		exit(1);
	}
	strcat(filename, USER_FILE);

	if(user_parseFile(filename, user_dict, &number, MAX_USER - 1) < 0) {
		fprintf(stderr, "user_readconf user_parseFile error ! \n");
		exit(1);
	}

	int blank = 0;
	for(int i = 0; i < number; i++) {
		DEBUGP5("number: %12s ; pass: %6s \n", user_dict[i].number, user_dict[i].pass);

		if(user_dict[i].number[0] == 0 || user_dict[i].pass[0] == 0) {
			blank++;
			continue;
		}

		int n = atoi(user_dict[i].number);
		int p = atoi(user_dict[i].pass);

		if(n == 0 || p == 0) {
			blank++;
			continue;
		}

		pp_user[i - blank].bidnumber   = n;
		pp_user[i - blank].bidpassword = p;
	}

	user_amount = number - blank;

	DEBUGP1("user.xml acount : %d , user_amount: %d \n\n", number, user_amount);
	LOGT1("user.xml acount : %d , user_amount: %d \n\n", number, user_amount);

	return 0 ;
}

// S0Z3NEAC850055
int user_initmem_machinecode(int max)
{
	char head[]   = "S0";
	char body[14] = {0};

	for(int i = 0; i < max; i++){
		myrand_getstr((unsigned char *)body, 14);
		sprintf(pp_user[i].machinecode, "%s%s", head, body);
	}

	return 0;
}

int user_initmem_event(int max)					// 初始化事件指针
{

	myevent_init(ev_login_start);
	myevent_init(ev_first_begin);
	myevent_init(ev_second_begin);
	myevent_init(ev_second_end);
	myevent_init(ev_bid0_image_shoot);
	myevent_init(ev_bid1_image_shoot);
	myevent_init(ev_bid1_image_warmup);
	myevent_init(ev_bid1_price_warmup);
	myevent_init(ev_bid2_image_shoot);
	myevent_init(ev_bid2_image_warmup);
	myevent_init(ev_bid2_price_warmup);

	for(int i = 0; i < max; i++){ 

		pp_user[i].session_login.event_login_req 	= ev_login_start;
		pp_user[i].session_login.event_login_ack	= &(pp_user[i].session_login._event_login_ack);

		pp_user[i].session_bid[0].event_image_req 	= ev_bid0_image_shoot;
		pp_user[i].session_bid[0].event_image_prereq 	= NULL;
		pp_user[i].session_bid[0].event_price_prereq 	= NULL;
		pp_user[i].session_bid[0].event_image_ack	= &(pp_user[i].session_bid[0]._event_image_ack);
		pp_user[i].session_bid[0].event_price_ack	= &(pp_user[i].session_bid[0]._event_price_ack);

		pp_user[i].session_bid[1].event_image_req 	= ev_bid1_image_shoot;
		pp_user[i].session_bid[1].event_image_prereq 	= ev_bid1_image_warmup;
		pp_user[i].session_bid[1].event_price_prereq 	= ev_bid1_price_warmup;
		pp_user[i].session_bid[1].event_image_ack	= &(pp_user[i].session_bid[1]._event_image_ack);
		pp_user[i].session_bid[1].event_price_ack	= &(pp_user[i].session_bid[1]._event_price_ack);

		pp_user[i].session_bid[2].event_image_req 	= ev_bid2_image_shoot;
		pp_user[i].session_bid[2].event_image_prereq 	= ev_bid2_image_warmup;
		pp_user[i].session_bid[2].event_price_prereq 	= ev_bid2_price_warmup;
		pp_user[i].session_bid[2].event_image_ack	= &(pp_user[i].session_bid[2]._event_image_ack);
		pp_user[i].session_bid[2].event_price_ack	= &(pp_user[i].session_bid[2]._event_price_ack);

		myevent_init(pp_user[i].session_login.event_login_ack);

		myevent_init(pp_user[i].session_bid[0].event_image_ack);
		myevent_init(pp_user[i].session_bid[0].event_price_ack);

		myevent_init(pp_user[i].session_bid[1].event_image_ack);
		myevent_init(pp_user[i].session_bid[1].event_price_ack);

		myevent_init(pp_user[i].session_bid[2].event_image_ack);
		myevent_init(pp_user[i].session_bid[2].event_price_ack);

	}

	return 0;
}

void user_clean_event(int max)
{
	myevent_clean(ev_login_start);
	myevent_clean(ev_first_begin);
	myevent_clean(ev_second_begin);
	myevent_clean(ev_second_end);
	myevent_clean(ev_bid0_image_shoot);
	myevent_clean(ev_bid1_image_shoot);
	myevent_clean(ev_bid1_image_warmup);
	myevent_clean(ev_bid1_price_warmup);
	myevent_clean(ev_bid2_image_shoot);
	myevent_clean(ev_bid2_image_warmup);
	myevent_clean(ev_bid2_price_warmup);

	for(int i = 0; i < max; i++){ 
		myevent_clean(pp_user[i].session_login.event_login_ack);

		myevent_clean(pp_user[i].session_bid[0].event_image_ack);
		myevent_clean(pp_user[i].session_bid[0].event_price_ack);

		myevent_clean(pp_user[i].session_bid[1].event_image_ack);
		myevent_clean(pp_user[i].session_bid[1].event_price_ack);

		myevent_clean(pp_user[i].session_bid[2].event_image_ack);
		myevent_clean(pp_user[i].session_bid[2].event_price_ack);
	}
}

int user_initmem_group(int max)
{
	for(int i = 0; i < max; i++){
		pp_user[i].group = i % 2;
	}
	return 0;
}

int user_initmem(int max)
{
	user_initmem_machinecode(max);

	user_initmem_event(max);

	user_initmem_group(max);

	return 0;
}

int user_init(void)
{
	memset(&pp_user,   0, sizeof(pp_user));

	user_readconf();
	user_initmem(user_amount);

	return 0;
}

void user_clean(void)
{
	user_clean_event(user_amount);
}

int user_print(int user_id)
{
	fprintf(stdout, "---------------------------------------------------------\n");
	fprintf(stdout, "user_id                                    = %d \n", user_id);
	fprintf(stdout, "group                                      = %d \n", pp_user[user_id].group);
	fprintf(stdout, "machinecode                                = %s \n", pp_user[user_id].machinecode);
	fprintf(stdout, "bidnumber                                  = %d \n", pp_user[user_id].bidnumber);
	fprintf(stdout, "bidpassword                                = %d \n", pp_user[user_id].bidpassword);
	fprintf(stdout, "price[0]                                   = %d \n", pp_user[user_id].price[0]);
	fprintf(stdout, "price[1]                                   = %d \n", pp_user[user_id].price[1]);
	fprintf(stdout, "price[2]                                   = %d \n", pp_user[user_id].price[2]);
	fprintf(stdout, "session_login.image                        = %d \n", pp_user[user_id].session_login.image);
	fprintf(stdout, "session_login.result_login.sid             = %s \n", pp_user[user_id].session_login.result_login.sid);
	fprintf(stdout, "session_login.result_login.name            = %s \n", pp_user[user_id].session_login.result_login.name);
	fprintf(stdout, "session_login.result_login.pid             = %s \n", pp_user[user_id].session_login.result_login.pid);
	fprintf(stdout, "session_bid[0].image                       = %d \n", pp_user[user_id].session_bid[0].image);
	fprintf(stdout, "session_bid[0].result_image.sid            = %s \n", pp_user[user_id].session_bid[0].result_image.sid); 
	fprintf(stdout, "session_bid[0].result_image.errcode        = %s \n", pp_user[user_id].session_bid[0].result_image.errcode);
	fprintf(stdout, "session_bid[0].result_image.errstr         = %s \n", pp_user[user_id].session_bid[0].result_image.errstr);
	//	fprintf(stdout, "session_bid[0].result_image.pic            = %s \n", pp_user[user_id].session_bid[0].result_image.pic);
	fprintf(stdout, "session_bid[0].result_price.sid            = %s \n", pp_user[user_id].session_bid[0].result_price.sid);
	fprintf(stdout, "session_bid[0].result_price.name           = %s \n", pp_user[user_id].session_bid[0].result_price.name);
	fprintf(stdout, "session_bid[0].result_price.pid            = %s \n", pp_user[user_id].session_bid[0].result_price.pid);
	fprintf(stdout, "session_bid[0].result_price.number         = %s \n", pp_user[user_id].session_bid[0].result_price.number);
	fprintf(stdout, "session_bid[0].result_price.count          = %s \n", pp_user[user_id].session_bid[0].result_price.count);
	fprintf(stdout, "session_bid[0].result_price.price          = %s \n", pp_user[user_id].session_bid[0].result_price.price);
	fprintf(stdout, "session_bid[0].result_price.time           = %s \n", pp_user[user_id].session_bid[0].result_price.time);
	fprintf(stdout, "session_bid[1].image                       = %d \n", pp_user[user_id].session_bid[1].image);
	fprintf(stdout, "session_bid[1].result_image.sid            = %s \n", pp_user[user_id].session_bid[1].result_image.sid); 
	fprintf(stdout, "session_bid[1].result_image.errcode        = %s \n", pp_user[user_id].session_bid[1].result_image.errcode);
	fprintf(stdout, "session_bid[1].result_image.errstr         = %s \n", pp_user[user_id].session_bid[1].result_image.errstr);
	//	fprintf(stdout, "session_bid[1].result_image.pic            = %s \n", pp_user[user_id].session_bid[1].result_image.pic);
	fprintf(stdout, "session_bid[1].result_price.sid            = %s \n", pp_user[user_id].session_bid[1].result_price.sid);
	fprintf(stdout, "session_bid[1].result_price.name           = %s \n", pp_user[user_id].session_bid[1].result_price.name);
	fprintf(stdout, "session_bid[1].result_price.pid            = %s \n", pp_user[user_id].session_bid[1].result_price.pid);
	fprintf(stdout, "session_bid[1].result_price.number         = %s \n", pp_user[user_id].session_bid[1].result_price.number);
	fprintf(stdout, "session_bid[1].result_price.count          = %s \n", pp_user[user_id].session_bid[1].result_price.count);
	fprintf(stdout, "session_bid[1].result_price.price          = %s \n", pp_user[user_id].session_bid[1].result_price.price);
	fprintf(stdout, "session_bid[1].result_price.time           = %s \n", pp_user[user_id].session_bid[1].result_price.time);
	fprintf(stdout, "session_bid[2].image                       = %d \n", pp_user[user_id].session_bid[2].image);
	fprintf(stdout, "session_bid[2].result_image.sid            = %s \n", pp_user[user_id].session_bid[2].result_image.sid); 
	fprintf(stdout, "session_bid[2].result_image.errcode        = %s \n", pp_user[user_id].session_bid[2].result_image.errcode);
	fprintf(stdout, "session_bid[2].result_image.errstr         = %s \n", pp_user[user_id].session_bid[2].result_image.errstr);
	//	fprintf(stdout, "session_bid[2].result_image.pic            = %s \n", pp_user[user_id].session_bid[2].result_image.pic);
	fprintf(stdout, "session_bid[2].result_price.sid            = %s \n", pp_user[user_id].session_bid[2].result_price.sid);
	fprintf(stdout, "session_bid[2].result_price.name           = %s \n", pp_user[user_id].session_bid[2].result_price.name);
	fprintf(stdout, "session_bid[2].result_price.pid            = %s \n", pp_user[user_id].session_bid[2].result_price.pid);
	fprintf(stdout, "session_bid[2].result_price.number         = %s \n", pp_user[user_id].session_bid[2].result_price.number);
	fprintf(stdout, "session_bid[2].result_price.count          = %s \n", pp_user[user_id].session_bid[2].result_price.count);
	fprintf(stdout, "session_bid[2].result_price.price          = %s \n", pp_user[user_id].session_bid[2].result_price.price);
	fprintf(stdout, "session_bid[2].result_price.time           = %s \n", pp_user[user_id].session_bid[2].result_price.time);
	fprintf(stdout, "---------------------------------------------------------\n");
	return 0;
}

