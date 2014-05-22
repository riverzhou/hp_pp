#!/usr/bin/env python3

from socketserver       import UDPServer, BaseRequestHandler
from time               import time, localtime, strftime, sleep
from abc                import ABCMeta, abstractmethod
from struct             import pack, unpack
from traceback          import print_exc
from hashlib            import md5
from xml.etree          import ElementTree
from threading          import Thread, Event, Lock, Semaphore

from pp_thread          import pp_subthread, pp_sender
from pp_log             import logger, printer

#-------------------------------------------

UDP_SERVER =('', 999)

Thread.daemon  = True
UDPServer.allow_reuse_address = True
UDPServer.request_queue_size  = 100

#================================================================================
'''
<TYPE>INFO</TYPE><INFO>A拍卖会：2014年4月19日上海市个人非营业性客车额度投标拍卖会
投放额度数：8200
本场拍卖会警示价：72600
拍卖会起止时间：10:30至11:30
首次出价时段：10:30至11:00
修改出价时段：11:00至11:30

          目前为首次出价时段
系统目前时间：10:39:50
目前已投标人数：77163
目前最低可成交价：100
最低可成交价出价时间：10:30:15</INFO>
'''
#-------------------------------------------------------------------------------=
'''
<TYPE>INFO</TYPE><INFO>B拍卖会：2014年4月19日上海市个人非营业性客车额度投标拍卖会
投放额度数：8200
目前已投标人数：94241
拍卖会起止时间：10:30至11:30
首次出价时段：10:30至11:00
修改出价时段：11:00至11:30

          目前为修改出价时段
系统目前时间：11:09:37
目前最低可成交价：72600
最低可成交价出价时间：10:30:08
目前修改价格区间：72300至72900</INFO>
'''
#================================================================================

class proto_udp():
        __metaclass__ = ABCMeta
        #strftime('%H:%M:%S',localtime(time()))

        @staticmethod
        def decode(data):
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

        @staticmethod
        def encode(data):
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

        @staticmethod
        def udp_make_format_ack(key_val):
                return ( ( (
                        '<TYPE>FORMAT</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        key_val['BIDNO'],
                        key_val['VCODE'],
                        ) ).encode('gb18030'),
                        key_val['addr']
                        )

        @staticmethod
        def udp_make_client_ack(key_val):
                return ( ( (
                        '<TYPE>CLIENT</TYPE>'+
                        '<BIDNO>%s</BIDNO>'+
                        '<VCODE>%s</VCODE>'
                        ) % (
                        key_val['BIDNO'],
                        key_val['VCODE'],
                        ) ).encode('gb18030'),
                        key_val['addr']
                        )

        @staticmethod
        def parse_ack(string):
                key_val = {}
                try:
                        xml_string = '<XML>' + string.strip() + '</XML>'
                        root = ElementTree.fromstring(xml_string)
                        for child in root:
                                key_val[child.tag] = child.text
                except :
                        logger.error(string)
                printer.info(string)
                printer.error(sorted(key_val.items()))
                printer.error('')
                return key_val

        def udp_make_a_info(self, key_val):
                return ( (
                        '<TYPE>INFO</TYPE><INFO>A拍卖会：2014年5月24日上海市个人非营业性客车额度投标拍卖会\r\n'+
                        '投放额度数：7400\r\n'+
                        '本场拍卖会警示价：72600\r\n'+
                        '拍卖会起止时间：10:30至11:30\r\n'+
                        '首次出价时段：10:30至11:00\r\n'+
                        '修改出价时段：11:00至11:30\r\n'+
                        '\r\n'+
                        '          目前为首次出价时段\r\n'+
                        '系统目前时间：%s\r\n'+
                        '目前已投标人数：%s\r\n'+
                        '目前最低可成交价：%s\r\n'+
                        '最低可成交价出价时间：$s</INFO>\r\n'
                        ) % (
                        key_val['time'],
                        key_val['number'],
                        key_val['price'],
                        key_val['time'],
                        ) ).encode('gb18030')

        def udp_make_b_info(self, key_val):
                return ( (
                        '<TYPE>INFO</TYPE><INFO>B拍卖会：2014年4月19日上海市个人非营业性客车额度投标拍卖会\r\n'+
                        '投放额度数：8200\r\n'+
                        '目前已投标人数：%s\r\n'+
                        '拍卖会起止时间：10:30至11:30\r\n'+
                        '首次出价时段：10:30至11:00\r\n'+
                        '修改出价时段：11:00至11:30\r\n'+
                        '\r\n'+
                        '          目前为修改出价时段\r\n'+
                        '系统目前时间：%s\r\n'+
                        '目前最低可成交价：%s\r\n'+
                        '最低可成交价出价时间：%s\r\n'+
                        '目前修改价格区间：%s至%s</INFO>\r\n'
                        ) % (
                        key_val['number'],
                        key_val['time'],
                        key_val['price'],
                        key_val['time'],
                        str(int(key_val['price']) - 300),
                        str(int(key_val['price']) + 300),
                        ) ).encode('gb18030')

#------------------------------------------------------

class info_maker(pp_subthread, proto_udp):
        def __init__(self):
                pp_subthread.__init__(self)
                proto_udp.__init__(self)

        def run(self):
                logger.debug('Thread %s : %s started' % (self.__class__.__name__, self.ident))
                self.started_set()
                try:
                        while True:
                                key_val = {}
                                #print(self.udp_make_a_info(key_val))
                                sleep(5)
                                key_val = {}
                                #print(self.udp_make_b_info(key_val))
                                sleep(5)
                except KeyboardInterrupt:
                        pass
                except :
                        print_exc()
                logger.debug('Thread %s : %s stoped' % (self.__class__.__name__, self.ident))

        def do_a_info(self):
                pass

        def do_b_info(self):
                pass


class buff_sender(pp_sender):

        def proc(self, buff):  # buff 为 (data, addr)
                data, addr = buff
                data = proto_udp.encode(data)
                server_udp.socket.sendto(data, addr)
                print(buff)
                print()

#------------------------------------------------------
class udp_handle(BaseRequestHandler):

        def handle(self):
                proto_dict = {
                        'FORMAT' : self.proc_format ,
                        'CLIENT' : self.proc_client ,
                        'LOGOUT' : self.proc_logout ,
                        }
                string = self.get()
                key_val = proto_udp.parse_ack(string)
                key_val['addr'] = self.client_address
                try:
                        proto_dict[key_val['TYPE']](key_val)
                except KeyError:
                        pass
                except:
                        print_exc()

        def get(self):
                return proto_udp.decode(self.request[0]).decode('gb18030')

        def proc_logout(self, key_val):
                #unreg
                pass

        def proc_format(self, key_val):
                #reg
                daemon_bs.put(proto_udp.udp_make_format_ack(key_val))

        def proc_client(self, key_val):
                daemon_bs.put(proto_udp.udp_make_client_ack(key_val))

#-------------------------------------------------------------------------------

daemon_im = info_maker()
daemon_bs = buff_sender()

#================================================================================

if __name__ == "__main__":
        daemon_im.start()
        daemon_im.started()
        daemon_bs.start()
        daemon_bs.started()
        server_udp = UDPServer(UDP_SERVER, udp_handle)
        server_udp.serve_forever()


