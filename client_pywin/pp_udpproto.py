#!/usr/bin/env python3

from struct                     import pack, unpack, pack_into, unpack_from
from traceback                  import print_exc
from hashlib                    import md5

from pp_log                     import logger, printer

#==================================================================================================================

class udp_proto():

        def parse_info_a(self, info):
                p1 = info.find('<INFO>') + len('<INFO>')
                p2 = info.find('</INFO>')
                info = info[p1:p2]
                info = info.split('^')
                key_val = {}
                key_val['code']         = 'A'
                key_val['systime']      = info[9]
                key_val['price']        = info[11]
                key_val['ltime']        = info[12]
                key_val['number']       = info[10]
                return key_val

        def parse_info_b(self, info):
                p1 = info.find('<INFO>') + len('<INFO>')
                p2 = info.find('</INFO>')
                info = info[p1:p2]
                info = info.split('^')
                key_val = {}
                key_val['code']         = 'B'
                key_val['systime']      = info[9]
                key_val['price']        = info[10]
                key_val['ltime']        = info[11]
                key_val['hprice']       = info[13]
                return  key_val

        def parse_info(self, info):
                if '<TYPE>INFO</TYPE><INFO>A' in info : return self.parse_info_a(info)
                if '<TYPE>INFO</TYPE><INFO>B' in info : return self.parse_info_b(info)
                return None

        def parse_ack(self, buff) :
                string = self.decode(buff).decode('gb18030')
                return self.parse_info(string)

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
                #printer.debug(format_req)
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
                #printer.debug(logoff_req)
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
                #printer.debug(client_req)
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
                if len2 != 0 : len1 += 1
                buff += b'\0\0\0\0'
                data = bytearray(len0 + 4)
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
                printer.debug(out)

#--------------------------------------------------------------------------------------

