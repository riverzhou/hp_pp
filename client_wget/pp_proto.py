#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from struct                     import pack, unpack
from traceback                  import print_exc
from hashlib                    import md5
from time                       import sleep
from xml.etree                  import ElementTree
import random, string

from pp_log                     import logger, printer

#==================================================================================================================

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

#------------------------------------------------------------------------------------------------------------------

class proto_udp():
        tag_dict = {
                '目前最低可成交价'      :  'price',
                '目前已投标人数'        :  'number',
                '系统目前时间'          :  'systime',
                '最低可成交价出价时间'  :  'lowtime',
                }

        def reg(self, client, login):
                self.client = client
                self.login  = login

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

        def parse_info(self, buff, echo = False):
                info_val = {}
                info = self.do_parse_ack(self.decode(buff).decode('gb18030'))['INFO']
                key_val = self.do_parse_info(info)
                for key in self.tag_dict :
                        info_val[self.tag_dict[key]] = key_val[key]
                if echo != False :
                        printer.debug(info)
                        printer.debug(sorted(info_val.items()))
                        printer.debug('')
                return info_val

        def do_parse_ack(self, string):
                key_val = {}
                try:
                        xml_string = '<XML>' + string.strip() + '</XML>'
                        root = ElementTree.fromstring(xml_string)
                        for child in root:
                                key_val[child.tag] = child.text
                except :
                        printer.error(string)
                return key_val

        def parse_ack(self, buff):
                string = self.decode(buff).decode('gb18030')
                key_val = self.do_parse_ack(string)
                printer.info(string)
                printer.info(sorted(key_val.items()))
                printer.info('')
                return key_val

        @staticmethod
        def print_bytes(buff):
                out     = ''
                for b in buff:
                        out += hex(b)
                        out += ' '
                print(out)

        @staticmethod
        def decode(buff):
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

        @staticmethod
        def encode(buff):
                return proto_udp.decode(buff)

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
                        self.get_vcode(self.login.pid, self.client.bidno)
                        ))
                printer.info(self.format_req)
                return self.format_req

        def do_logoff_req(self):
                self.logoff_req = ((
                        '<TYPE>LOGOFF</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        self.client.bidno,
                        self.get_vcode(self.login.pid, self.client.bidno)
                        ))
                printer.info(self.logoff_req)
                return self.logoff_req

        def do_client_req(self):
                self.client_req = ((
                        '<TYPE>CLIENT</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        self.client.bidno,
                        self.get_vcode(self.login.pid, self.client.bidno)
                        ))
                printer.info(self.client_req)
                return self.client_req

        def make_format_req(self):
                return proto_udp.encode(self.do_format_req().encode('gb18030'))

        def make_logoff_req(self):
                return proto_udp.encode(self.do_logoff_req().encode('gb18030'))

        def make_client_req(self):
                return proto_udp.encode(self.do_client_req().encode('gb18030'))

#--------------------------------------------------------------------------------------

class proto_ssl():
        __metaclass__ = ABCMeta

        agent   = 'Mozilla/3.0+(compatible;+IndyLibrary)'
        version = '177'

        @abstractmethod
        def make_req(self):pass

        def parse_ack(self, string):
                html_string, xml_string = self.split_html_xml_from_string(string)
                self.ack = (self.get_dict_from_xml(xml_string), self.get_sid_from_html(html_string))
                return self.ack

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

        def split_html_xml_from_string(self, string):
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
                        self.version, 
                        bidcode, 
                        image, 
                        self.client.mcode
                        ))
                return self.get_md5(seed)

        def get_login_checkcode(self):
                return self.get_price_checkcode(0, self.client.loginimage)

        def get_image_checkcode(self, price):
                number = ('%d'
                        % (
                        int(self.client.bidno) - int(price)
                        ))
                seed = ('%s#%s@%s'
                        % (
                        number, 
                        self.version, 
                        self.client.passwd
                        ))
                return self.get_md5(seed)

        def get_wget_req(self, key_val):
                path   = key_val['path']
                host   = key_val['host']
                self.wget_req = ((
                        'https://%s%s'
                        ) % (
                        host, path
                        ))
                #print(self.wget_req)
                return self.wget_req.encode()

        def get_py_req(self, key_val):
                path   = key_val['path']
                host   = key_val['host']
                sid    = key_val['sid']
                self.req = ((
                        'GET '+
                        '%s'+
                        ' HTTP/1.0\r\n'+
                        'Content-Type: text/html\r\n'+
                        'Host: %s:443\r\n'+
                        'Accept: text/html, */*\r\n'+
                        'User-Agent: %s\r\n'+
                        '%s'+
                        '\r\n'
                        ) % (
                        path,
                        host,
                        self.agent,
                        '' if sid == '' else ('Cookie: JSESSIONID=%s\r\n' % sid)
                        ))
                printer.info(self.req)
                return self.req.encode('gb18030')
                
class proto_ssl_login(proto_ssl):
        ack_len = 4096

        def reg(self, client, login, server):
                self.client  = client
                self.login   = login
                self.server  = server

        def get_login_path(self, image):
                return ((
                        '/car/gui/login.aspx'+
                        '?BIDNUMBER=%s'+                                                # 8
                        '&BIDPASSWORD=%s'+                                              # 4
                        '&MACHINECODE=%s'+                                              # ~
                        '&CHECKCODE=%s'+                                                # 32
                        '&VERSION=%s'+                                                  # 3
                        '&IMAGENUMBER=%s'                                               # 6
                        ) % (
                        self.client.bidno, 
                        self.client.passwd, 
                        self.client.mcode, 
                        self.get_login_checkcode(), 
                        self.version, 
                        image
                        ))

        def make_wget_req(self, image):
                key_val = {}
                key_val['host']    = self.server
                key_val['path']    = self.get_login_path(image)
                return self.get_wget_req(key_val)

        def make_req(self, image):
                key_val = {}
                key_val['host']    = self.server
                key_val['path']    = self.get_login_path(image)
                key_val['sid']     = ''
                return self.get_py_req(key_val)

        def parse_ack(self, buff):
                string = buff.decode('gb18030')
                proto_ssl.parse_ack(self, string)
                key_val = {}
                key_val['name'] = self.ack[0]['CLIENTNAME']
                key_val['pid'] = self.ack[0]['PID']
                key_val['sid'] = self.ack[1]
                printer.info(string)
                printer.warning(sorted(key_val.items()))
                printer.warning('')
                return key_val

class proto_ssl_image(proto_ssl):
        ack_len = 8192

        def reg(self, client, bid, server):
                self.client = client
                self.bid    = bid
                self.server = server

        def get_image_path(self, price):
                return ((
                        '/car/gui/imagecode.aspx'+
                        '?BIDNUMBER=%s'+                                                # 8
                        '&BIDPASSWORD=%s'+                                              # 4
                        '&BIDAMOUNT=%s'+                                                # ~
                        '&VERSION=%s'+                                                  # 3
                        '&CHECKCODE=%s'                                                 # 32
                        ) % (
                        self.client.bidno,
                        self.client.passwd,
                        price,
                        self.version,
                        self.get_image_checkcode(price)
                        ))

        def make_wget_req(self, price):
                key_val = {}
                key_val['host']    = self.server
                key_val['path']    = self.get_image_path(price)
                return self.get_wget_req(key_val)

        def make_req(self, price, sid):
                key_val = {}
                key_val['host']    = self.server
                key_val['path']    = self.get_image_path(price)
                key_val['sid']     = sid
                return self.get_py_req(key_val)

        def parse_ack(self, buff):
                string = buff.decode('gb18030')
                proto_ssl.parse_ack(self, string)
                key_val = {}
                key_val['image'] = self.ack[0]['IMAGE_CONTENT']
                key_val['sid'] = self.ack[1]
                info_val = {}
                info_val['errcode'] = self.ack[0]['ERRORCODE']
                info_val['errstr'] = self.ack[0]['ERRORSTRING']
                info_val['sid'] = self.ack[1]
                printer.debug(string)
                #printer.warning(sorted(key_val.items()))
                printer.warning(sorted(info_val.items()))
                printer.warning('')
                return key_val

class proto_ssl_price(proto_ssl):
        ack_len = 4096

        def reg(self, client, bid, server):
                self.client = client
                self.bid    = bid
                self.server = server

        def get_price_path(self, price, image):
                return ((
                        '/car/gui/bid.aspx'+
                        '?BIDNUMBER=%s'+                                                # 8
                        '&BIDPASSWORD=%s'+                                              # 4
                        '&BIDAMOUNT=%s'+                                                # ~
                        '&MACHINECODE=%s'+
                        '&CHECKCODE=%s'+                                                # 32
                        '&VERSION=%s'+
                        '&IMAGENUMBER=%s'                                               # 6
                        ) % (
                        self.client.bidno,
                        self.client.passwd,
                        price,
                        self.client.mcode,
                        self.get_price_checkcode(price, image),
                        self.version,
                        image
                        ))

        def make_wget_req(self, price, image):
                key_val = {}
                key_val['host']    = self.server
                key_val['path']    = self.get_price_path(price, image)
                return self.get_wget_req(key_val)

        def make_req(self, price, image, sid):
                key_val = {}
                key_val['host']    = self.server
                key_val['path']    = self.get_price_path(price, image)
                key_val['sid']     = sid
                return self.get_py_req(key_val)

        def parse_ack(self, buff):
                string = buff.decode('gb18030')
                proto_ssl.parse_ack(self, string)
                key_val = {}
                key_val['time'] = self.ack[0]['BIDTIME']
                key_val['count'] = self.ack[0]['BIDCOUNT']
                key_val['price'] = self.ack[0]['BIDAMOUNT']
                key_val['name'] = self.ack[0]['CLIENTNAME']
                key_val['bidno'] = self.ack[0]['BIDNUMBER']
                key_val['sid'] = self.ack[1]
                printer.info(string)
                printer.warning(sorted(key_val.items()))
                printer.warning('')
                return key_val

#--------------------------------------------------------------------------------------

class proto_client_bid():
        __metaclass__ = ABCMeta

        def __init__(self, client):
                self.bidno      = client.bidno
                self.client     = client

class proto_client_login():
        __metaclass__ = ABCMeta

        def __init__(self, client):
                self.bidno      = client.bidno
                self.client     = client

class proto_client():
        __metaclass__ = ABCMeta

        def __init__(self, user, machine):
                self.user       = user
                self.bidno      = user.bidno
                self.passwd     = user.passwd
                self.mcode      = machine.mcode
                self.loginimage = machine.loginimage
               
class proto_machine():
        def __init__(self, mcode = '', loginimage = ''):
                self.mcode      = mcode if mcode != '' else proto_machine.create_mcode()
                self.loginimage = loginimage if loginimage != '' else proto_machine.create_number()

        @staticmethod
        def create_mcode():
                return ''.join([(string.ascii_letters+string.digits)[x] for x in random.sample(range(0,62),random.randint(10,20))])

        @staticmethod
        def create_number():
                return ''.join([(string.digits)[x] for x in random.sample(range(0,10),6)])

#================================= for test ===========================================

if __name__ == "__main__":
        pass


