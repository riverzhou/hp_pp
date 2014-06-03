#!/usr/bin/env python3

from struct                     import pack, unpack
from traceback                  import print_exc
from hashlib                    import md5
from xml.etree                  import ElementTree

from pp_log                     import logger, printer

#==================================================================================================================

class udp_proto():
        tag_dict = {
                '目前最低可成交价'      :  'price',
                '目前已投标人数'        :  'number',
                '系统目前时间'          :  'systime',
                '最低可成交价出价时间'  :  'lowtime',
                }

        def __init__(self, client, login):
                self.client = client
                self.login = login
                self.udp_ack = []
                self.info_ack = []

        #-----------------------------------------------------

        def do_parse_info(self, info):
                key_val = {}
                key_val['CODE'] = info[0]
                if key_val['CODE'] != 'A' and key_val['CODE'] != 'B' : return None
                for line in info.split('\n') :
                        data = line.split('：', 1)
                        key_val[data[0].strip()] = data[1].strip() if len(data) == 2
                return key_val

        def parse_info(self, buff, echo = False):
                info_val = {}
                info = self.do_parse_ack(self.decode(buff).decode('gb18030'))['INFO']
                key_val = self.do_parse_info(info)
                if key_val == None : return None
                try:
                        for key in self.tag_dict:  info_val[self.tag_dict[key]] = key_val[key]
                except KeyError:
                        printer.error(sorted(key_val.items()))
                if echo != False :
                        printer.debug(info)
                        printer.debug(sorted(info_val.items()))
                        printer.debug('')
                return info_val

        #-----------------------------------------------------

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

        def parse_ack(self, buff,  echo = False):
                string = self.decode(buff).decode('gb18030')
                key_val = self.do_parse_ack(string)
                if echo != False :
                        printer.debug(string)
                        printer.debug(sorted(key_val.items()))
                        printer.debug('')
                return key_val

        #-----------------------------------------------------

        def do_format_req(self, bidno, pid):
                format_req = ((
                        '<TYPE>FORMAT</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        bidno,
                        self.get_vcode(pid, bidno)
                        ))
                printer.info(format_req)
                return format_req.encode('gb18030')

        def do_logoff_req(self, bidno, pid):
                logoff_req = ((
                        '<TYPE>LOGOFF</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        bidno,
                        self.get_vcode(pid, bidno)
                        ))
                printer.info(logoff_req)
                return logoff_req.encode('gb18030')

        def do_client_req(self, bidno, pid):
                client_req = ((
                        '<TYPE>CLIENT</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        bidno,
                        self.get_vcode(pid, bidno)
                        ))
                printer.info(client_req)
                return client_req.encode('gb18030')

        def make_format_req(self, bidno, pid):
                return self.encode(self.do_format_req(bidno, pid))

        def make_logoff_req(self, bidno, pid):
                return self.encode(self.do_logoff_req(bidno, pid))

        def make_client_req(self, bidno, pid):
                return self.encode(self.do_client_req(bidno, pid))

        #-----------------------------------------------------

        def get_md5_up(self, string):
                return md5(string.encode()).hexdigest().upper()

        def get_vcode(self, pid, bidno):
                return self.get_md5_up(pid + bidno)

        def decode(self, buff):
                len0 = len(buff)
                len1 = len0 // 4
                len2 = len0 % 4
                if len2 != 0:
                        len1 += 1
                        buff += b'\0\0\0'
                data = bytearray(len0+len2)
                view = memoryview(data)
                buff = memoryview(buff)
                for i in range(len1) :
                        offset = i*4
                        pack_into('i', view, offset, ~unpack_from('i', buff, offset)[0])
                data = bytes(data[0:len0])
                return data

        def encode(self, buff):
                return self.decode(buff)

        def print_bytes(self, buff):
                out     = ''
                for b in buff:
                        out += hex(b)
                        out += ' '
                print(out)

#--------------------------------------------------------------------------------------

