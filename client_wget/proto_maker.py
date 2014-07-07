#!/usr/bin/env python3

#==========================================================

import sys

from pp_sslproto        import *
from pp_server          import server_dict

#==========================================================

wget_user_dict    = {
                     '52219990' : '3319' ,
                     '52131206' : '1706' ,
                    }

wget_server_group = 0                   # 0/1 , 选择服务器组

wget_machinecode  = 'ABCDEFGHI'         
#wget_machinecode = ''                  # 为空串表示自动生成随机特征码
wget_loginimage   = ''

wget_agent        = 'Mozilla/3.0 (compatible; Indy Library)'

#==========================================================

def proc_login(argv):
        global wget_user_dict, wget_machinecode, wget_loginimage, server_dict, wget_server_group

        if len(argv) != 3:
                return usage()
        bidno = argv[2]
        
        if not bidno in wget_user_dict :
                return print('unknow bidno')

        machine = proto_machine(wget_machinecode, wget_loginimage)

        key_val = {}
        key_val['bidno']        = bidno
        key_val['passwd']       = wget_user_dict[bidno]
        key_val['mcode']        = machine.mcode
        key_val['login_image']  = machine.image
        key_val['host_name']    = server_dict[wget_server_group]['login']['name']

        main_write_file('login.req', proto_ssl_login(key_val).make_wget_login_req(key_val['host_name']))
        main_wget_cmd('login')

def proc_image(argv):
        global wget_user_dict, wget_machinecode, wget_loginimage

        if len(argv) != 4:
                return usage()
        bidno = argv[2]
        price = argv[3]

        if not bidno in wget_user_dict :
                return print('unknow bidno')

        machine = proto_machine(wget_machinecode, wget_loginimage)

        key_val = {}
        key_val['bidno']        = bidno
        key_val['passwd']       = wget_user_dict[bidno]
        key_val['mcode']        = machine.mcode
        key_val['host_name']    = server_dict[wget_server_group]['toubiao']['name']

        main_write_file('image.req', proto_ssl_image(key_val).make_wget_image_req(key_val['host_name'], price))
        main_wget_cmd('image', 'login')

def proc_price(argv):
        global wget_user_dict, wget_machinecode, wget_loginimage

        if len(argv) != 5:
                return usage()
        bidno = argv[2]
        price = argv[3]
        image = argv[4]

        if not bidno in wget_user_dict :
                return print('unknow bidno')

        machine = proto_machine(wget_machinecode, wget_loginimage)

        key_val = {}
        key_val['bidno']        = bidno
        key_val['passwd']       = wget_user_dict[bidno]
        key_val['mcode']        = machine.mcode
        key_val['host_name']    = server_dict[wget_server_group]['toubiao']['name']

        main_write_file('price.req', proto_ssl_price(key_val).make_wget_price_req(key_val['host_name'], price, image))
        main_wget_cmd('price', 'image')

#---------------------------------------

def main_wget_cmd(operate, load = ''):
        global wget_agent
        wget_cmd = ((
                'wget'+
                ' --no-check-certificate'+
                ' -U "%s"'+
                ' -i %s.req'+
                ' -O %s.ack'+
                ' --save-cookies=%s.cookie'+
                ' --keep-session-cookies'+
                ' %s'
                ) % (
                wget_agent,
                operate,
                operate,
                operate,
                '' if load == '' else ('--load-cookies=%s.cookie' % load)
                ))
        print(wget_cmd)
        return wget_cmd

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
        string = './proto_maker.py login 12345678'
        print(string)
        string = './proto_maker.py image 12345678 74000'
        print(string)
        string = './proto_maker.py price 12345678 74000 123456'
        print(string)
                        
#----------------------------------------------------------

def pp_test(argv):
        if len(argv) <= 2 :
                return usage()
        if not argv[1] in func_list :
                return usage()
        func_list[argv[1]](argv)

#----------------------------------------------------------

if __name__ == "__main__":
        pp_test(sys.argv)

