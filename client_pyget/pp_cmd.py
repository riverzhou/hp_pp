#!/usr/bin/env python3

#==========================================================

from socket             import gethostbyname
from pickle             import dump, load
from traceback          import print_exc
import sys

from pp_log             import logger, printer
from pp_https           import pyget
from pp_sslproto        import *
from pic_viewer         import show_photo

#==========================================================

pyget_user_dict    = {
                     '12345678' : '1234' ,
                     '98765432' : '4321' ,
                    }

pyget_server_group = 1                   # 1/2 , 选择服务器组

pyget_machinecode  = ''                  # 为空串表示自动生成随机特征码
pyget_loginimage   = ''

#==========================================================

def proc_login(argv):
        global pyget_user_dict, pyget_machinecode, pyget_loginimage

        if len(argv) != 3:
                return usage()
        bidno = argv[2]
        
        if not bidno in pyget_user_dict :
                return print('unknow bidno')

        machine = proto_machine(pyget_machinecode, pyget_loginimage)

        key_val = {}
        key_val['bidno']        = bidno
        key_val['passwd']       = pyget_user_dict[bidno]
        key_val['mcode']        = machine.mcode
        key_val['login_image']  = machine.image
        key_val['host_name']    = login_server
        key_val['host_ip']      = gethostbyname(login_server)

        proto    = proto_ssl_login(key_val)
        print(proto.make_ssl_head())
        info_val = pyget(login_server, proto.make_login_req(), proto.make_ssl_head())
        print(sorted(info_val.items()))
        print()
        print()

        if info_val['status'] != 200 :
                print('ack status error!!!')
                print(sorted(info_val.items()))
                print()
                return

        ack_sid  = proto.get_sid_from_head(info_val['head'])
        ack_val  = proto.parse_login_ack(info_val['body'])
        print(ack_sid, sorted(ack_val.items()))
        print()

        return ack_sid, ack_val

def proc_image(argv):
        global pyget_user_dict, pyget_machinecode, pyget_loginimage

        if len(argv) != 4:
                return usage()
        bidno = argv[2]
        price = argv[3]

        if not bidno in pyget_user_dict :
                return print('unknow bidno')

        machine = proto_machine(pyget_machinecode, pyget_loginimage)

        key_val = {}
        key_val['bidno']        = bidno
        key_val['passwd']       = pyget_user_dict[bidno]
        key_val['mcode']        = machine.mcode
        #key_val['login_image']  = machine.image
        key_val['host_name']    = image_server
        key_val['host_ip']      = gethostbyname(image_server)

        proto    = proto_ssl_image(key_val)
        info_val = pyget(image_server, proto.make_image_req(price), proto.make_ssl_head())
        print(sorted(info_val.items()))
        print()
        print()

        if info_val['status'] != 200 :
                print('ack status error!!!')
                print(sorted(info_val.items()))
                print()
                return

        ack_sid  = proto.get_sid_from_head(info_val['head'])
        ack_val  = proto.parse_image_ack(info_val['body'])
        database.db['image_sid'] = ack_sid
        print(ack_sid, sorted(ack_val.items()))
        print()

        show_photo(ack_val['image'])

        return ack_sid, ack_val

def proc_price(argv):
        global pyget_user_dict, pyget_machinecode, pyget_loginimage

        if len(argv) != 5:
                return usage()
        bidno = argv[2]
        price = argv[3]
        image = argv[4]

        if not bidno in pyget_user_dict :
                return print('unknow bidno')

        machine = proto_machine(pyget_machinecode, pyget_loginimage)

        key_val = {}
        key_val['bidno']        = bidno
        key_val['passwd']       = pyget_user_dict[bidno]
        key_val['mcode']        = machine.mcode
        #key_val['login_image']  = machine.image
        key_val['host_name']    = image_server
        key_val['host_ip']      = gethostbyname(image_server)

        image_sid = database.db['image_sid']  if 'image_sid' in database.db else None
        if image_sid == None :
                print('no image_sid')
                print()

        proto    = proto_ssl_price(key_val)
        info_val = pyget(price_server, proto.make_price_req(price, image), proto.make_ssl_head(image_sid))
        print(sorted(info_val.items()))
        print()
        print()

        if info_val['status'] != 200 :
                print('ack status error!!!')
                print(sorted(info_val.items()))
                print()
                return

        ack_sid  = proto.get_sid_from_head(info_val['head'])
        ack_val  = proto.parse_price_ack(info_val['body'])
        print(ack_sid, sorted(ack_val.items()))
        print()

        return ack_sid, ack_val

#---------------------------------------

def main_init_dns():
        global login_server, price_server, image_server, pyget_server_group, pp_server_dict, pp_server_dict_2
        server_dict = pp_server_dict if pyget_server_group == 1 else pp_server_dict_2
        login_server = server_dict['login'][0]
        image_server = server_dict['toubiao'][0]
        price_server = server_dict['toubiao'][0]

def main_write_file(name, buff):
        f = open(name, 'wb')
        f.write(buff)
        f.close()

#----------------------------------------------------------

func_list =     {
                'login' : proc_login,
                'image' : proc_image,
                'price' : proc_price,
                }

def usage():
        string = './pp_cmd.py login 12345678'
        print(string)
        string = './pp_cmd.py image 12345678 74000'
        print(string)
        string = './pp_cmd.py price 12345678 74000 123456'
        print(string)
                        
#----------------------------------------------------------

class DataBase():
        pass

database = DataBase()
db_name  = 'pp_db.dump'

#-----------------------------------------------------------

def load_dump():
        global db_name, database
        try:
                f = open(db_name, 'rb')
                database = load(f)
                f.close()
                logger.info('DataBase Loaded')
                #print(database.db)
        except FileNotFoundError:
                database.db = {}
                logger.info('DataBase Created')
        except:
                print_exc()

def save_dump():
        global db_name, database
        try:
                f = open(db_name, 'wb')
                dump(database, f, 4)
                f.close()
                logger.info('DataBase Saved')
                #print(database.db)
        except:
                print_exc()

#----------------------------------------------------------

def pp_cmd(argv):
        if len(argv) <= 2 :
                return usage()
        if not argv[1] in func_list :
                return usage()
        load_dump()
        main_init_dns()
        func_list[argv[1]](argv)
        save_dump()

if __name__ == "__main__":
        pp_cmd(sys.argv)

