#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from struct                     import pack, unpack
from socket                     import socket
from traceback                  import print_exc
from time                       import time, localtime, strftime
from hashlib                    import md5
from time                       import sleep
from socket                     import gethostbyname
from xml.etree                  import ElementTree
import random, string

from pp_log                     import make_log

#======================================================================================

pp_server_dict = {
        'login'    : ('tblogin.alltobid.com',   443),
        'toubiao'  : ('toubiao.alltobid.com',   443),
        'result'   : ('tbresult.alltobid.com',  443),
        'query'    : ('tbquery.alltobid.com',   443),
        'udp'      : ('tbudp.alltobid.com',     999),
}

pp_server_dict_2 = {
        'login'    : ('tblogin2.alltobid.com',  443),
        'toubiao'  : ('toubiao2.alltobid.com',  443),
        'result'   : ('tbresult2.alltobid.com', 443),
        'query'    : ('tbquery2.alltobid.com',  443),
        'udp'      : ('tbudp2.alltobid.com',    999),
}

pp_price_list = ('73800','73900','74000','74100','74200','74300','74400','74500')

#--------------------------------------------------------------------------------------

class proto_udp():
        def __init__(self, client, login):
                self.client = client
                self.login = login
                self.udp_ack = []
                self.info_ack = []

        def do_parse_info(self, info):
                key_val = {}
                key_val['CODE'] = info[0]
                if key_val['CODE'] == 'C' :
                        return key_val
                info = info[1:]
                for line in info.split('\n') :
                        line = line.strip()
                        if '：' in line:
                                data = line.split('：',1)
                                key_val[data[0].strip()] = data[1].strip()
                return key_val

        def parse_info(self, buff):
                info = self.do_parse_ack(self.decode(buff).decode('gb18030'))['INFO']
                key_val = self.do_parse_info(info)
                self.info_ack.append(key_val)
                return key_val

        def do_print_info(self, string):
                info = self.do_parse_ack(string)['INFO']
                print()
                print(info)
                print(self.do_parse_info(info))
                print()

        def print_info(self, buff):
                info = self.do_parse_ack(self.decode(buff).decode('gb18030'))['INFO']
                print()
                print(info)
                print(self.do_parse_info(info))
                print()

        def do_parse_ack(self, string):
                key_val = {}
                try:
                        xml_string = '<XML>' + string.strip() + '</XML>'
                        root = ElementTree.fromstring(xml_string)
                        for child in root:
                                key_val[child.tag] = child.text
                except :
                        print(string)
                return key_val

        def parse_ack(self, buff):
                key_val = self.do_parse_ack(self.decode(buff).decode('gb18030'))
                self.udp_ack.append(key_val)
                return key_val

        def do_print_ack(self, string):
                print()
                print(string)
                print(self.do_parse_ack(string))
                print()

        def print_ack(self, buff):
                print()
                print(self.decode(buff).decode('gb18030'))
                print(self.do_parse_ack(self.decode(buff).decode('gb18030')))
                print()

        def print_buff(self, buff):
                print()
                self.print_bytes(buff)
                print()

        def print_encode_buff(self, buff):
                print()
                self.print_bytes(self.decode(buff))
                print()

        def print_bytes(self, buff):
                out     = ''
                for b in buff:
                        out += hex(b)
                        out += ' '
                print(out)

        def decode(self, buff):
                data = b''
                len0 = len(buff)
                len1 = len0 // 4
                len2 = len0 % 4
                if len2 != 0:
                        len1 += 1
                for i in range(4 - len2):
                        buff += b'0'
                for i in range(len1) :
                        data += pack('i', ~unpack('i', buff[i*4:i*4+4])[0])
                data = data[0:len0]
                return data

        def encode(self, buff):
                return self.decode(buff)

        def get_md5_up(self, string):
                return md5(string.encode()).hexdigest().upper()

        def get_vcode(self, pid, bidno):
                return self.get_md5_up(pid + bidno)

        def do_format_req(self):
                self.format_req = ((
                        '<TYPE>FORMAT</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        self.client.bidno,
                        self.get_vcode(self.login.proto_ssl_login.pid, self.client.bidno)
                        )).encode()
                return self.format_req                        

        def do_logoff_req(self):
                self.logoff_req = ((
                        '<TYPE>LOGOFF</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        self.client.bidno,
                        self.get_vcode(self.login.proto_ssl_login.pid, self.client.bidno)
                        )).encode()
                return self.logoff_req

        def do_client_req(self):
                self.client_req = ((
                        '<TYPE>CLIENT</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        self.client.bidno,
                        self.get_vcode(self.login.proto_ssl_login.pid, self.client.bidno)
                        )).encode()
                return self.client_req

        def make_format_req(self):
                return self.encode(self.do_format_req())

        def make_logoff_req(self):
                return self.encode(self.do_logoff_req())

        def make_client_req(self):
                return self.encode(self.do_client_req())

        def print_encode_format_req(self):
                print()
                self.print_bytes(self.make_format_req())
                print()

        def print_encode_logoff_req(self):
                print()
                self.print_bytes(self.make_logoff_req())
                print()

        def print_encode_client_req(self):
                print()
                self.print_bytes(self.make_client_req())
                print()

        def print_format_req(self):
                print()
                print(self.do_format_req())
                print()

        def print_logoff_req(self):
                print()
                print(self.do_logoff_req())
                print()

        def print_client_req(self):
                print()
                print(self.do_client_req())
                print()

#--------------------------------------------------------------------------------------

class proto_ssl():
        __metaclass__ = ABCMeta

        @abstractmethod
        def make_req(self):pass

        def parse_ack(self, buff):
                html_string, xml_string = self.split_html_xml_from_buff(buff)
                self.ack = (self.get_dict_from_xml(xml_string), self.get_sid_from_html(html_string))
                return self.ack

        def print_req(self):
                print()
                print(self.make_req())
                print()

        def print_ack(self, buff):
                print()
                html_string, xml_string = self.split_html_xml_from_buff(buff)
                print(xml_string.strip())
                print(self.get_dict_from_xml(xml_string), self.get_sid_from_html(html_string))
                print()

        def get_sid_from_html(self, html_string):
                p1 = html_string.find('JSESSIONID')
                s1 = html_string[p1:]
                p2 = s1.find(';')
                s2 = s1[0:p2]
                p3 = s2.find('=')
                s3 = s2[p3+1:]
                return s3.strip()

        def get_dict_from_xml(self, xml_string):
                key_val = {}
                root = ElementTree.fromstring(xml_string)
                for child in root:
                        key_val[child.tag] = child.text
                return key_val

        def split_html_xml_from_buff(self, buff):
                string = buff.decode()
                p = string.find('<XML>')
                return (string[0:p], string[p:])

        def get_md5(self, string):
                return md5(string.encode()).hexdigest()

        def get_bidcode_md5_to_md8(self,string):
                p = (3,5,11,13,19,21,27,29)
                md8 = ''
                for i in p :
                        md8 += string[i-1]
                return md8

        def get_bidcode(self, price):
                c = int(self.client.bidno) - int(self.client.passwd) + int(price)
                c = c >> 4
                if c == 1000 :
                        c += 1000;
                code_md5_seed = '%d' % c
                code_md5 = self.get_md5(code_md5_seed)
                code_md8 = self.get_bidcode_md5_to_md8(code_md5)
                return code_md8

        def get_price_checkcode(self, price, image):
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
                return self.get_price_checkcode(0, self.client.loginimage_number)

        def get_image_checkcode(self, price):
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
        def __init__(self, client, login):
                self.client = client
                self.login = login
                self.ack_len = 4096

        def make_req(self):
                self.req = ((
                        'GET /car/gui/login.aspx'+
                        '?BIDNUMBER=%s'+                                                # 8
                        '&BIDPASSWORD=%s'+                                              # 4
                        '&MACHINECODE=%s'+                                              # ~
                        '&CHECKCODE=%s'+                                                # 32
                        '&VERSION=%s'+                                                  # 3
                        '&IMAGENUMBER=%s'+                                              # 6
                        ' HTTP/1.0\r\n'+
                        'Content-Type: text/html\r\n'+
                        'Host: %s:443\r\n'+                                             # ~
                        'Accept: text/html, */*\r\n'+
                        'User-Agent: Mozilla/3.0 (compatible; IndyLibrary)\r\n\r\n'
                        ) % (
                        self.client.bidno, 
                        self.client.passwd, 
                        self.client.mcode, 
                        self.get_login_checkcode(), 
                        self.client.version, 
                        self.client.loginimage_number,
                        self.client.server_dict['login']['name']
                        )).encode()
                return self.req

        def parse_ack(self, buff):
                proto_ssl.parse_ack(self, buff)
                self.name = self.ack[0]['CLIENTNAME']
                self.pid = self.ack[0]['PID']
                self.sid = self.ack[1]

class proto_ssl_image(proto_ssl):
        def __init__(self, client, bid, bidid):
                self.client = client
                self.bid = bid
                self.bidid = bidid
                self.ack_len = 8192

        def make_req(self):
                self.req = ((
                        'GET /car/gui/imagecode.aspx'+
                        '?BIDNUMBER=%s'+                                                # 8
                        '&BIDPASSWORD=%s'+                                              # 4
                        '&BIDAMOUNT=%s'+                                                # ~
                        '&VERSION=%s'+                                                  # 3
                        '&CHECKCODE=%s'+                                                # 32
                        ' HTTP/1.0\r\n'+
                        'Content-Type: text/html\r\n'+
                        'Host: %s:443\r\n'+                                             # ~
                        'Accept: text/html, */*\r\n'+
                        'User-Agent: Mozilla/3.0 (compatible; Indy Library)\r\n'+
                        'Cookie: JSESSIONID=%s\r\n\r\n'                                 # 32
                        ) % (
                        self.client.bidno,
                        self.client.passwd,
                        self.bid.price_amount,
                        self.client.version,
                        self.get_image_checkcode(self.bid.price_amount),
                        self.client.server_dict['toubiao']['name'],
                        self.client.login.proto_ssl_login.sid
                        )).encode()
                return self.req                        

        def parse_ack(self, buff):
                proto_ssl.parse_ack(self, buff)
                self.bid.image_pic = self.ack[0]['IMAGE_CONTENT']
                self.bid.sid = self.ack[1]

class proto_ssl_price(proto_ssl):
        def __init__(self, client, bid, bidid):
                self.client = client
                self.bid = bid
                self.bidid = bidid
                self.ack_len = 4096

        def make_req(self):
                self.req = ((
                        'GET /car/gui/bid.aspx'+
                        '?BIDNUMBER=%s'+                                                # 8
                        '&BIDPASSWORD=%s'+                                              # 4
                        '&BIDAMOUNT=%s'+                                                # ~
                        '&MACHINECODE=%s'+
                        '&CHECKCODE=%s'+                                                # 32
                        '&VERSION=%s'+
                        '&IMAGENUMBER=%s'+                                              # 6
                        ' HTTP/1.0\r\n'+
                        'Content-Type: text/html\r\n'+
                        'Host: %s:443\r\n'+                                             # ~
                        'Accept: text/html, */*\r\n'+
                        'User-Agent: Mozilla/3.0 (compatible; Indy Library)\r\n'+
                        'Cookie: JSESSIONID=%s\r\n\r\n'                                 # 32
                        ) % (
                        self.client.bidno,
                        self.client.passwd,
                        self.bid.price_amount,
                        self.client.mcode,
                        self.get_price_checkcode(self.bid.price_amount, self.bid.image_number),
                        self.client.version,
                        self.bid.image_number,
                        self.client.server_dict['toubiao']['name'],
                        self.bid.sid
                        )).encode()
                return self.req

        def parse_ack(self, buff):
                proto_ssl.parse_ack(self, buff)
                self.bid.time = self.ack[0]['BIDTIME']
                self.bid.count = self.ack[0]['BIDCOUNT']

#--------------------------------------------------------------------------------------

class proto_bid_price():
        __metaclass__ = ABCMeta

        def __init__(self, client, bid, bidid):
                self.client = client
                self.bid = bid
                self.bidid = bidid
                self.proto_ssl_price = proto_ssl_price(client, bid, bidid)

class proto_bid_image():
        __metaclass__ = ABCMeta

        def __init__(self, client, bid, bidid):
                self.client = client
                self.bid = bid
                self.bidid = bidid
                self.proto_ssl_image = proto_ssl_image(client, bid, bidid)

class proto_client_bid():
        __metaclass__ = ABCMeta

        def __init__(self, client, bidid):
                global pp_price_list
                self.client = client
                self.bidid = bidid
                self.price_dict = {}.fromkeys(pp_price_list)

class proto_client_login():
        __metaclass__ = ABCMeta

        def __init__(self, client):
                self.client = client
                self.proto_udp = proto_udp(client, self)
                self.proto_ssl_login = proto_ssl_login(client, self)

class proto_pp_client():
        __metaclass__ = ABCMeta

        def __init__(self, user, machine, server_dict):
                self.bidno = user.bidno
                self.passwd = user.passwd
                self.mcode = machine.mcode
                self.loginimage_number = machine.loginimage_number
                self.server_dict = server_dict
                self.version = '177'
               
#================================= for test ===========================================

pp_user_dict       = {}
pp_machine_dict    = {}
pp_client_dict     = {}

class pp_user():
        def __init__(self, bidno = '', passwd = ''):
                self.bidno = bidno
                self.passwd = passwd

class pp_machine():
        def __init__(self, mcode = '', loginimage_number = ''):
                if mcode != '':
                        self.mcode = mcode
                else:
                        self.mcode = self.create_mcode()

                if loginimage_number != '':
                        self.loginimage_number = loginimage_number
                else:
                        self.loginimage_number = self.create_number()

        def create_mcode(self):
                return ''.join([(string.ascii_letters+string.digits)[x] for x in random.sample(range(0,62),random.randint(10,20))])

        def create_number(self):
                return ''.join([(string.digits)[x] for x in random.sample(range(0,10),6)])

#--------------------------------- for test -------------------------------------------

class bid_price(proto_bid_price):
        def __init__(self, client, bid, bidid):
                proto_bid_price.__init__(self, client, bid, bidid)

class bid_image(proto_bid_image):
        def __init__(self, client, bid, bidid):
                proto_bid_image.__init__(self, client, bid, bidid)
                
class client_bid(proto_client_bid):
        def __init__(self, client, bidid):
                proto_client_bid.__init__(self, client, bidid)
                self.image = bid_image(client, self, bidid)
                self.price = bid_price(client, self, bidid)

                self.image_number = '111111'
                self.price_amount = '555'
                self.sid = 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'

class client_login(proto_client_login):
        def __init__(self, client):
                proto_client_login.__init__(self, client)

                self.proto_ssl_login.pid = '111111111111111111'
                self.proto_ssl_login.sid = 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'

class pp_client(proto_pp_client):
        def __init__(self, user, machine, server_dict):
                proto_pp_client.__init__(self, user, machine, server_dict)
                self.login = client_login(self)
                self.bid = []
                for i in range(3):
                        self.bid.append(client_bid(self, i))

                self.mcode = 'VVVVVVVVVVVVVVVVVVV'
                self.loginimage_number = '333333'

#--------------------------------- for test -------------------------------------------

def pp_init_config():
        global pp_bidno_dict
        pp_user_dict['88888888']  = pp_user('88888888','4444')
        pp_machine_dict['88888888'] = pp_machine()

def pp_init_dns():
        global pp_server_dict, pp_server_dict_2
        for s in pp_server_dict :
                pp_server_dict[s]  = {
                                        'addr' : (gethostbyname(pp_server_dict[s][0]), pp_server_dict[s][1]),
                                        'name' : pp_server_dict[s][0]}

def pp_init_client():
        global pp_client_dict, pp_user_dict
        for bidno in pp_user_dict:
                if not bidno in pp_client_dict:
                        pp_client_dict[bidno] = pp_client(pp_user_dict[bidno], pp_machine_dict[bidno], pp_server_dict)

def pp_print_req():
        global pp_client_dict, pp_user_dict
        for bidno in pp_user_dict:
                pp_client_dict[bidno].login.proto_ssl_login.print_req()
                pp_client_dict[bidno].bid[0].image.proto_ssl_image.print_req()
                pp_client_dict[bidno].bid[0].price.proto_ssl_price.print_req()

                pp_client_dict[bidno].login.proto_udp.print_format_req()
                pp_client_dict[bidno].login.proto_udp.print_logoff_req()
                pp_client_dict[bidno].login.proto_udp.print_client_req()

                pp_client_dict[bidno].login.proto_udp.print_encode_format_req()
                pp_client_dict[bidno].login.proto_udp.print_encode_logoff_req()
                pp_client_dict[bidno].login.proto_udp.print_encode_client_req()

def pp_print_ack():
        global pp_client_dict, pp_user_dict
        for bidno in pp_user_dict:
                pp_client_dict[bidno].login.proto_ssl_login.print_ack(pp_read_file_to_buff('login.ack'))
                pp_client_dict[bidno].bid[0].image.proto_ssl_image.print_ack(pp_read_file_to_buff('image.ack'))
                pp_client_dict[bidno].bid[0].price.proto_ssl_price.print_ack(pp_read_file_to_buff('price.ack'))

                pp_client_dict[bidno].login.proto_udp.do_print_ack(pp_read_file_to_buff('udp_format.ack').decode().strip())
                pp_client_dict[bidno].login.proto_udp.do_print_info(pp_read_file_to_buff('udp_info.ack').decode('gb18030'))
                print(pp_read_file_to_buff('udp_info.ack'))

def pp_read_file_to_buff(name):
        buff = b''
        f = open(name, 'rb')
        try:
                buff = f.read()
        finally:
                f.close()
        return buff

def pp_main():
        pp_init_config()
        pp_init_dns()
        pp_init_client()
        #pp_print_req()
        pp_print_ack()

if __name__ == "__main__":
        pp_main()


