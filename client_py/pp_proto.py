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

#--------------------------------------------------------------------------------------

class proto_udp():
        def __init__(self, client, login):
                self.client = client
                self.login = login
                self.udp_ack = []

        def parse_ack(self, string):
                key_val = {}
                try:
                        xml_string = '<XML>' + string.strip() + '</XML>'
                        root = ElementTree.fromstring(xml_string)
                        for child in root:
                                key_val[child.tag] = child.text
                except :
                        print(string)
                self.udp_ack.append(key_val)
                return key_val

        def parse_encode_ack(self, buff):
                return self.parse_ack(self.decode(buff).decode())

        def print_buff(self, buff):
                print(buff.decode())
                print(self.parse_ack(buff.decode()))

        def print_encode_buff(self, buff):
                print(self.decode(buff).decode())
                print(self.parse_encode_ack(buff))

        def print_ack(self, buff):
                print(self.parse_ack(buff))

        def print_encode_ack(self, buff):
                print(self.parse_encode_ack(buff))

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

        def get_vcode(self, uid, bidno):
                return self.get_md5_up(uid + bidno)

        def make_format_req(self):
                self.format_req = ((
                        '<TYPE>FORMAT</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        self.client.bidno,
                        self.get_vcode(self.login.uid, self.client.bidno)
                        ))
                return self.format_req                        

        def make_logoff_req(self):
                self.logoff_req = ((
                        '<TYPE>LOGOFF</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        self.client.bidno,
                        self.get_vcode(self.login.uid, self.client.bidno)
                        ))
                return self.logoff_req

        def make_client_req(self):
                self.client_req = ((
                        '<TYPE>CLIENT</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        self.client.bidno,
                        self.get_vcode(self.login.uid, self.client.bidno)
                        ))
                return self.client_req

        def encode_format_req(self):
                return self.encode(self.make_format_req().encode())

        def encode_logoff_req(self):
                return self.encode(self.make_logoff_req().encode())

        def encode_client_req(self):
                return self.encode(self.make_client_req().encode())

        def print_encode_format_req(self):
                self.print_bytes(self.encode_format_req())

        def print_encode_logoff_req(self):
                self.print_bytes(self.encode_logoff_req())

        def print_encode_client_req(self):
                self.print_bytes(self.encode_client_req())

        def print_format_req(self):
                print(self.make_format_req())

        def print_logoff_req(self):
                print(self.make_logoff_req())

        def print_client_req(self):
                print(self.make_client_req())

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
                print(self.make_req())

        def print_ack(self, buff):
                print(self.parse_ack(buff))

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
                        self.client.server_dict['login'][2] 
                        ))
                return self.req                        

class proto_ssl_image(proto_ssl):
        def __init__(self, client, bid, bidid):
                self.client = client
                self.bid = bid
                self.bidid = bidid

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
                        self.client.server_dict['toubiao'][2],
                        self.bid.session_id
                        ))
                return self.req                        

class proto_ssl_price(proto_ssl):
        def __init__(self, client, bid, bidid):
                self.client = client
                self.bid = bid
                self.bidid = bidid

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
                        self.client.server_dict['toubiao'][2],
                        self.bid.session_id
                        ))
                return self.req                        

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
                self.client = client
                self.bidid = bidid
                self.image_number = '666666'
                self.price_amount = '100'
                self.session_id = '8899CF08D15BE46A7872A443D865A5D5'

class proto_client_login():
        __metaclass__ = ABCMeta

        def __init__(self, client):
                self.client = client
                self.uid = '310108195810053456'
                self.proto_udp = proto_udp(client, self)
                self.proto_ssl_login = proto_ssl_login(client, self)

class proto_pp_client():
        __metaclass__ = ABCMeta

        def __init__(self, bidno_dict, server_dict):
                self.bidno = bidno_dict[0]
                self.passwd = bidno_dict[1]
                self.server_dict = server_dict
                self.version = '177'
                self.mcode = 'VB8c560dd2-2de8b7c4'
                self.loginimage_number = '666666'
               
#================================= for test ===========================================

pp_bidno_dict   = {}
pp_client_dict  = {}

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

                self.image_number = '928393'
                self.price_amount = '500'
                self.session_id = '8899CF08D15BE46A7872A443D865A5D5'

class client_login(proto_client_login):
        def __init__(self, client):
                proto_client_login.__init__(self, client)

class pp_client(proto_pp_client):
        def __init__(self, bidno_dict, server_dict):
                proto_pp_client.__init__(self,bidno_dict, server_dict)
                self.login = client_login(self)
                self.bid = []
                for i in range(3):
                        self.bid.append(client_bid(self, i))
                self.mcode = 'VB8c560dd2-2de8b7c4'
                self.loginimage_number = '372318'

#--------------------------------------------------------------------------------------

def pp_init_config():
        global pp_bidno_dict
        #pp_bidno_dict['98765432']  = ('98765432','4321')
        pp_bidno_dict['88888888']  = ('88888888','4444')

def pp_init_dns():
        global pp_server_dict
        for s in pp_server_dict :
                pp_server_dict[s] = (gethostbyname(pp_server_dict[s][0]), pp_server_dict[s][1], pp_server_dict[s][0])

def pp_init_client():
        global pp_client_dict, pp_bidno_dict
        for bidno in pp_bidno_dict:
                if not bidno in pp_client_dict:
                        pp_client_dict[bidno] = pp_client(pp_bidno_dict[bidno],pp_server_dict)

def pp_print_req():
        global pp_client_dict, pp_bidno_dict
        for bidno in pp_bidno_dict:
                pp_client_dict[bidno].login.proto_ssl_login.print_req()
                pp_client_dict[bidno].bid[0].image.proto_ssl_image.print_req()
                pp_client_dict[bidno].bid[0].price.proto_ssl_price.print_req()
                pp_client_dict[bidno].login.proto_udp.print_format_req()
                pp_client_dict[bidno].login.proto_udp.print_logoff_req()
                pp_client_dict[bidno].login.proto_udp.print_client_req()

def pp_print_ack():
        global pp_client_dict, pp_bidno_dict
        for bidno in pp_bidno_dict:
                pp_client_dict[bidno].login.proto_ssl_login.print_ack(pp_read_file_to_buff('login.ack'))
                pp_client_dict[bidno].bid[0].image.proto_ssl_image.print_ack(pp_read_file_to_buff('image.ack'))
                pp_client_dict[bidno].bid[0].price.proto_ssl_price.print_ack(pp_read_file_to_buff('price.ack'))
                pp_client_dict[bidno].login.proto_udp.print_ack(pp_read_file_to_buff('udp_format.ack').decode())
                pp_client_dict[bidno].login.proto_udp.print_ack(pp_read_file_to_buff('udp_logoff.req').decode())

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


