#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from threading                  import Thread
from multiprocessing            import Process, Event, Condition, Lock, Event
from struct                     import pack, unpack
from socketserver               import TCPServer, BaseRequestHandler
from socket                     import socket
from traceback                  import print_exc
from time                       import time, localtime, strftime
from hashlib                    import md5
from time                       import sleep
from socket                     import socket, gethostbyname, AF_INET, SOCK_STREAM, SOCK_DGRAM

#======================================================================================

class proto_udp():
        __metaclass__ = ABCMeta

        def __init__(self,client):
                self.client = client

        def decode(self,buff):
                pass

        def encode(self,buff):
                return self.decode(buff)

        def print(self,buff):
                print(self.decode(buff))

class proto_udp_login(proto_udp):
        def __init__(self,client):
                super(proto_udp_login,self).__init__(client)

        def make_req(self):
                pass

        def parse_ack(self):
                pass

class proto_udp_logoff(proto_udp):
        def __init__(self,client):
                super(proto_udp_login,self).__init__(client)

        def make_req(self):
                pass

        def parse_ack(self):
                pass

#--------------------------------------------------------------------------------------

class proto_ssl():
        __metaclass__ = ABCMeta

        def __init__(self,client):
                self.client = client

        def make_req(self):
                return ''

        def parse_ack(self):
                return ''

        def print_req(self):
                print(self.make_req())

        def print_ack(self):
                print(self.parse_ack())

class proto_ssl_login(proto_ssl):
        def make_req(self):
                return 'GET /car/gui/login.aspx?BIDNUMBER=%s&BIDPASSWORD=%s&MACHINECODE=%s&CHECKCODE=%s&VERSION=%s&IMAGENUMBER=%s HTTP/1.0\r\nContent-Type: text/html\r\nHost: %s:443\r\nAccept: text/html, */*\r\nUser-Agent: Mozilla/3.0 (compatible; IndyLibrary)\r\n\r\n' % (self.client.bidno, self.client.passwd, self.client.mcode, self.get_checkcode(), self.client.version, self.client.loginimage, self.client.server_dict['login'][2])

        def get_checkcode(self):
                seed = 'aaaaaaaaaa'
                #return md5(seed.encode()).hexdigest().upper()
                return md5(seed.encode()).hexdigest()


class proto_ssl_image(proto_ssl):
        def __init__(self,client):
                super(proto_ssl_image,self).__init__(client)


class proto_ssl_price(proto_ssl):
        def __init__(self,client):
                super(proto_ssl_price,self).__init__(client)



#================================= for test ===========================================

pp_server_dict = {
        'login'    : ('tblogin.alltobid.com',   443),
        'toubiao'  : ('toubiao.alltobid.com',   443),
        'result'   : ('tbresult.alltobid.com',  443),
        'query'    : ('tbquery.alltobid.com',   443),
        'udp'      : ('tbudp.alltobid.com',     999),
}

pp_bidno_dict   = {}
pp_client_dict  = {}

class pp_client():
        def __init__(self,bidno_dict,server_dict):
                self.bidno = bidno_dict[0]
                self.passwd = bidno_dict[1]
                self.server_dict = server_dict
                self.mcode = 'S0D123456abcd'
                self.version = '177'
                self.loginimage = '001122'
                self.proto_udp_login = proto_udp_login(self)
                self.proto_ssl_login = proto_ssl_login(self)
                self.proto_ssl_image = proto_ssl_image(self)
                self.proto_ssl_price = proto_ssl_price(self)

def pp_init_config():
        global pp_bidno_dict
        pp_bidno_dict['98765432']  = ('98765432','4321')
        pp_bidno_dict['98765431']  = ('98765431','1321')

def pp_init_dns():
        global pp_server_dict
        for s in pp_server_dict :
                pp_server_dict[s] = (gethostbyname(pp_server_dict[s][0]), pp_server_dict[s][1], pp_server_dict[s][0])

def pp_init_client():
        global pp_client_dict, pp_bidno_dict
        for bidno in pp_bidno_dict:
                if not bidno in pp_client_dict:
                        pp_client_dict[bidno] = pp_client(pp_bidno_dict[bidno],pp_server_dict)

def pp_print_login_req():
        global pp_client_dict, pp_bidno_dict
        for bidno in pp_bidno_dict:
                pp_client_dict[bidno].proto_ssl_login.print_req()

def pp_main():
        pp_init_config()
        pp_init_dns()
        pp_init_client()
        pp_print_login_req()

if __name__ == "__main__":
        try:
                pp_main()
        except  KeyboardInterrupt:
                pass


