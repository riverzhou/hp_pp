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

        def get_md5_up(self, string):
                return md5(string.encode()).hexdigest().upper()

        def get_vcode(self):
                return self.get_md5_up(self.client.uid + self.client.bidno)
 
        def decode(self,data):
                buff = b''
                len0 = len(data)
                len1 = len0 // 4
                len2 = len0 % 4
                if len2 != 0:
                        len1 += 1
                for i in range(4 - len2):
                        data += b'0'
                for i in range(len1) :
                        buff += pack('i', ~unpack('i', data[i*4:i*4+4])[0])
                buff = buff[0:len0]
                return buff

        def encode(self,buff):
                return self.decode(buff)

        def print_bytes(self, buff):
                out     = ''
                for b in buff:
                        out += hex(b)
                        out += ' '
                print(out)

        def print(self,buff):
                print(self.decode(buff).decode())

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

        @abstractmethod
        def make_req(self):pass

        @abstractmethod
        def parse_ack(self):pass

        def print_req(self):
                print(self.make_req())

        def print_ack(self):
                print(self.parse_ack())

        def get_md5(self,string):
                return md5(string.encode()).hexdigest()

        def get_bidcode_md5_to_md8(self,string):
                p = (3,5,11,13,19,21,27,29)
                md8 = ''
                for i in p :
                        md8 += string[i-1]
                return md8

        def get_bidcode(self,price):
                c = int(self.client.bidno) - int(self.client.passwd) + int(price)
                c = c >> 4
                if c == 1000 :
                        c += 1000;
                code_md5_seed = '%d' % c
                code_md5 = self.get_md5(code_md5_seed)
                code_md8 = self.get_bidcode_md5_to_md8(code_md5)
                return code_md8

        def get_price_checkcode(self,price,image):
                bidcode = self.get_bidcode(price)
                seed = ('%s%s%s%sAAA'
                        % (
                        self.client.version, 
                        bidcode, 
                        image, 
                        self.client.mcode
                        ))
                return self.get_md5(seed)

        def get_login_checkcode(self):
                return self.get_price_checkcode(0, self.client.loginimage)

        def get_image_checkcode(self,price):
                number = ('%d'
                        % (
                        int(self.client.bidno) - int(price)
                        ))
                seed = ('%s#%s@%s'
                        % (
                        number, 
                        self.client.version, 
                        self.client.passwd
                        ))
                return self.get_md5(seed)

class proto_ssl_login(proto_ssl):
        def make_req(self):
                return ((
                        'GET /car/gui/login.aspx'+
                        '?BIDNUMBER=%s'+                # 8
                        '&BIDPASSWORD=%s'+              # 4
                        '&MACHINECODE=%s'+              # ~
                        '&CHECKCODE=%s'+                # 32
                        '&VERSION=%s'+                  # 3
                        '&IMAGENUMBER=%s'+              # 6
                        ' HTTP/1.0\r\n'+
                        'Content-Type: text/html\r\n'+
                        'Host: %s:443\r\n'+             # ~
                        'Accept: text/html, */*\r\n'+
                        'User-Agent: Mozilla/3.0 (compatible; IndyLibrary)\r\n\r\n'
                        ) % (
                        self.client.bidno, 
                        self.client.passwd, 
                        self.client.mcode, 
                        self.get_login_checkcode(), 
                        self.client.version, 
                        self.client.loginimage,
                        self.client.server_dict['login'][2] 
                        ))

        def parse_ack(self):
                pass

class proto_ssl_image(proto_ssl):
        def __init__(self,client):
                super(proto_ssl_image,self).__init__(client)

        def make_req(self):
                pass

        def parse_ack(self):
                pass

        def get_checkcode(self):
                pass

class proto_ssl_price(proto_ssl):
        def __init__(self,client):
                super(proto_ssl_price,self).__init__(client)

        def make_req(self):
                pass

        def parse_ack(self):
                pass

        def get_checkcode(self):
                pass

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
                self.mcode = 'VB8c560dd2-2de8b7c4'
                self.version = '177'
                self.loginimage = '272772'
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
        pp_main()


