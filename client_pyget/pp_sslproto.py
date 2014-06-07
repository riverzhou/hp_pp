#!/usr/bin/env python3

#from traceback                  import print_exc
from struct                     import pack, unpack
from hashlib                    import md5
from xml.etree                  import ElementTree

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

#==================================================================================================================

base64_kv =    {
        '0':  ord('A'),
        '1':  ord('B'),
        '2':  ord('C'),
        '3':  ord('D'),
        '4':  ord('E'),
        '5':  ord('F'),
        '6':  ord('G'),
        '7':  ord('H'),
        '8':  ord('I'),
        '9':  ord('J'),
        'A':  ord('K'),
        'B':  ord('L'),
        'C':  ord('M'),
        'D':  ord('N'),
        'E':  ord('O'),
        'F':  ord('P'),
        'G':  ord('Q'),
        'H':  ord('R'),
        'I':  ord('S'),
        'J':  ord('T'),
        'K':  ord('U'),
        'L':  ord('V'),
        'M':  ord('W'),
        'N':  ord('X'),
        'O':  ord('Y'),
        'P':  ord('Z'),
        'Q':  ord('a'),
        'R':  ord('b'),
        'S':  ord('c'),
        'T':  ord('d'),
        'U':  ord('e'),
        'V':  ord('f'),
        'W':  ord('g'),
        'X':  ord('h'),
        'Y':  ord('i'),
        'Z':  ord('j'),
        'a':  ord('k'),
        'b':  ord('l'),
        'c':  ord('m'),
        'd':  ord('n'),
        'e':  ord('o'),
        'f':  ord('p'),
        'g':  ord('q'),
        'h':  ord('r'),
        'i':  ord('s'),
        'j':  ord('t'),
        'k':  ord('u'),
        'l':  ord('v'),
        'm':  ord('w'),
        'n':  ord('x'),
        'o':  ord('y'),
        'p':  ord('z'),
        'q':  ord('0'),
        'r':  ord('1'),
        's':  ord('2'),
        't':  ord('3'),
        'u':  ord('4'),
        'v':  ord('5'),
        'w':  ord('6'),
        'x':  ord('7'),
        'y':  ord('8'),
        'z':  ord('9'),
        '+':  ord('+'),
        '/':  ord('/'),
        }

#------------------------------------------------------------------------------------------------------------------

class proto_ssl():
        login_ack_len = 4096
        price_ack_len = 4096
        image_ack_len = 8192

        version = '177'
        agent   = 'Mozilla/3.0+(compatible;+IndyLibrary)'

        def __init__(self, key_val):
                self.mcode       = key_val['mcode']         if 'mcode'       in key_val  else None
                self.bidno       = key_val['bidno']         if 'bidno'       in key_val  else None
                self.passwd      = key_val['passwd']        if 'passwd'      in key_val  else None
                self.login_image = key_val['login_image']   if 'login_image' in key_val  else None
                self.login_pid   = key_val['login_pid']     if 'login_pid'   in key_val  else None
                self.login_sid   = key_val['login_sid']     if 'login_sid'   in key_val  else None
                self.image_sid   = key_val['image_sid']     if 'image_sid'   in key_val  else None
                self.host_name   = key_val['host_name']     if 'host_name'   in key_val  else None
                self.host_ip     = key_val['host_ip']       if 'host_ip'     in key_val  else None

        def make_header(self, sessionid = None):
                '''
                ' HTTP/1.0\r\n'+
                'Content-Type: text/html\r\n'+
                'Host: %s:443\r\n'+
                'Accept: text/html, */*\r\n'+
                'User-Agent: Mozilla/3.0 (compatible; IndyLibrary)\r\n\r\n'
                '''

        def get_wget_req(self, host, path):
                return (('https://%s%s') % (host, path.decode('gb18030'))).encode()

        #-------------------------------------------

        def parse_ssl_ack(self, string):
                #printer.debug(string)
                xml_string = string.strip()
                key_val = {}
                try:
                        root = ElementTree.fromstring(xml_string)
                        for child in root:
                                key_val[child.tag] = child.text
                except :
                        printer.error(xml_string)
                if key_val == {} :
                        printer.error(xml_string)
                return key_val

        def get_price_checkcode(self, price, image):
                seed = ('%s%s%s%sAAA'
                        % (
                        self.version, 
                        self.get_bidcode(self.bidno, self.passwd, price),
                        image, 
                        self.mcode
                        ))
                return self.get_md5(seed)

        def get_login_checkcode(self):
                return self.get_price_checkcode(0, self.login_image)

        def get_image_checkcode(self, price):
                seed = ('%d#%s@%s'
                        % (
                        int(self.bidno) - int(price),
                        self.version, 
                        self.passwd
                        ))
                return self.get_md5(seed)

        def image_decode(self, string):
                global  base64_kv
                key_val = base64_kv
                size    = len(string)
                output  = bytearray(size)
                for i in range(size):
                        output[i] = key_val[string[i]]
                return output.decode()

        #----------------------------------------------

        def get_md5(self, string):
                return md5(string.encode()).hexdigest()

        def get_bidcode_md5_to_md8(self, string):
                p = (3,5,11,13,19,21,27,29)
                md8 = ''
                for i in p :
                        md8 += string[i-1]
                return md8

        def get_bidcode(self, bidno, passwd,  price):
                c = int(bidno) - int(passwd) + int(price)
                c = c >> 4
                if c == 1000 :
                        c += 1000;
                code_md5_seed = '%d' % c
                code_md5 = self.get_md5(code_md5_seed)
                code_md8 = self.get_bidcode_md5_to_md8(code_md5)
                return code_md8

#----------------------------------------------

class proto_ssl_login(proto_ssl):
        def make_login_req(self):
                return ((
                        '/car/gui/login.aspx'+
                        '?BIDNUMBER=%s'+                                                # 8
                        '&BIDPASSWORD=%s'+                                              # 4
                        '&MACHINECODE=%s'+                                              # ~
                        '&CHECKCODE=%s'+                                                # 32
                        '&VERSION=%s'+                                                  # 3
                        '&IMAGENUMBER=%s'                                               # 6
                        ) % (
                        self.bidno,
                        self.passwd,
                        self.mcode,
                        self.get_login_checkcode(image),
                        self.version,
                        self.login_image
                        )).encode('gb18030')

        def make_wget_login_req(self):
                return self.get_wget_req(host_name, self.make_login_req())

        def parse_login_ack(self, buff):
                string   = buff.decode('gb18030')
                info_val = self.parse_ssl_ack(string)
                key_val  = {}
                key_val['name'] = info_val['CLIENTNAME']
                key_val['pid']  = info_val['PID']
                #key_val['sid']  = ''                    # XXX TODO XXX  从包头的分析中得到
                printer.info(string)
                printer.info(sorted(key_val.items()))
                printer.info('')
                return key_val

#----------------------------------------------

class proto_ssl_image(proto_ssl):
        def make_image_req(self, price):
                return ((
                        '/car/gui/imagecode.aspx'+
                        '?BIDNUMBER=%s'+                                                # 8
                        '&BIDPASSWORD=%s'+                                              # 4
                        '&BIDAMOUNT=%s'+                                                # ~
                        '&VERSION=%s'+                                                  # 3
                        '&CHECKCODE=%s'                                                 # 32
                        ) % (
                        self.bidno,
                        self.passwd,
                        price,
                        self.version,
                        self.get_image_checkcode(price)
                        )).encode('gb18030')

        def make_wget_image_req(self, price):
                return self.get_wget_req(host_name, self.make_image_req(price))

        def parse_image_ack(self, buff):
                string   = buff.decode('gb18030')
                info_val = self.parse_ssl_ack(string)
                key_val  = {}
                key_val['image']   = self.image_decode(info_val['IMAGE_CONTENT'])
                key_val['errcode'] = info_val['ERRORCODE']
                key_val['errstr']  = info_val['ERRORSTRING']
                #key_val['sid']  = ''                    # XXX TODO XXX  从包头的分析中得到
                printer.info(string)
                printer.info(sorted(key_val.items()))
                printer.info('')
                return key_val

#----------------------------------------------

class proto_ssl_price(proto_ssl):
        def make_price_req(self, price, image):
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
                        self.bidno,
                        self.passwd,
                        price,
                        self.mcode,
                        self.get_price_checkcode(price, image),
                        self.version,
                        image
                        )).encode('gb18030')

        def make_wget_price_req(self, price, image):
                return self.get_wget_req(host_name, self.make_price_req(price, image))

        def parse_price_ack(self, buff):
                string   = buff.decode('gb18030')
                info_val = self.parse_ssl_ack(string)
                key_val  = {}
                key_val['time']  = info_val['BIDTIME']
                key_val['count'] = info_val['BIDCOUNT']
                key_val['price'] = info_val['BIDAMOUNT']
                key_val['name']  = info_val['CLIENTNAME']
                key_val['bidno'] = info_val['BIDNUMBER']
                #key_val['sid']  = ''                    # XXX TODO XXX  从包头的分析中得到
                printer.info(string)
                printer.info(sorted(key_val.items()))
                printer.info('')
                return key_val

#----------------------------------------------


