#!/usr/bin/env python3

#==========================================================

import sys

from pp_proto       import *

#==========================================================

wget_user_dict    = {
                     '12345678' : '1234' ,
                     '98765432' : '4321' ,
                    }

wget_server_group = 1                   # 1/2 , 选择服务器组

wget_machinecode  = 'ABCDEFGHI'         
#wget_machinecode = ''                  # 为空串表示自动生成随机特征码
wget_loginimage   = ''

wget_agent        = 'Mozilla/3.0+(compatible;+IndyLibrary)'

#==========================================================
#----------------------------------------------------------

class worker_login(proto_ssl_login):
        pass

class worker_image(proto_ssl_image):
        pass

class worker_price(proto_ssl_price):
        pass

#----------------------------------------------------------

class wget_client_bid(proto_client_bid):
        def __init__(self, client):
                proto_client_bid.__init__(self, client)

                global price_server, image_server
                self.image   = worker_image()
                self.price   = worker_price()
                self.image.reg(client, self, image_server)
                self.price.reg(client, self, price_server)

class wget_client_login(proto_client_login):
        def __init__(self, client):
                proto_client_login.__init__(self, client)

                global login_server
                self.ssl     = worker_login()
                self.ssl.reg(client, self, login_server)

class wget_client(proto_client):
        def __init__(self, user, machine):
                proto_client.__init__(self, user, machine)

                self.login   = wget_client_login(self)
                self.bid     = wget_client_bid(self)

class wget_machine(proto_machine):
        pass

class wget_user():
        def __init__(self, bidno, passwd, machine = None):
                self.bidno   = bidno
                self.passwd  = passwd
                self.machine = machine if machine != None else wget_machine()
                self.client  = wget_client(self, self.machine)

#==========================================================

def proc_login(argv):
        global wget_user_dict, wget_machinecode, wget_loginimage

        if len(argv) != 3:
                return usage()
        bidno = argv[2]
        
        if not bidno in wget_user_dict :
                return print('unknow bidno')

        passwd  = wget_user_dict[bidno]
        machine = wget_machine(wget_machinecode, wget_loginimage)
        user    = wget_user(bidno, passwd, machine)
        main_write_file('login.req', user.client.login.ssl.make_wget_req(user.client.loginimage))
        main_wget_cmd('login')

def proc_image(argv):
        global wget_user_dict, wget_machinecode, wget_loginimage

        if len(argv) != 4:
                return usage()
        bidno = argv[2]
        price = argv[3]

        if not bidno in wget_user_dict :
                return print('unknow bidno')

        passwd  = wget_user_dict[bidno]
        machine = wget_machine(wget_machinecode, wget_loginimage)
        user    = wget_user(bidno, passwd, machine)
        main_write_file('image.req', user.client.bid.image.make_wget_req(price))
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

        passwd  = wget_user_dict[bidno]
        machine = wget_machine(wget_machinecode, wget_loginimage)
        user    = wget_user(bidno, passwd, machine)
        main_write_file('price.req', user.client.bid.price.make_wget_req(price, image))
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

def main_init_dns():
        global login_server, price_server, image_server, wget_server_group, pp_server_dict, pp_server_dict_2
        server_dict = pp_server_dict if wget_server_group == 1 else pp_server_dict_2
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
        #main_init_dump()
        main_init_dns()
        func_list[argv[1]](argv)
        #main_write_dump()

#----------------------------------------------------------

if __name__ == "__main__":
        pp_test(sys.argv)

