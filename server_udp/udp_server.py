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
from pp_log             import logger 

#-------------------------------------------

UDP_SERVER =('', 999)

Thread.daemon  = True
UDPServer.allow_reuse_address = True
UDPServer.request_queue_size  = 100

#================================================================================

class proto_udp():
        __metaclass__ = ABCMeta

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
        def parse_ack(string):
                key_val = {}
                try:
                        xml_string = '<XML>' + string.strip() + '</XML>'
                        root = ElementTree.fromstring(xml_string)
                        for child in root:
                                key_val[child.tag] = child.text
                except :
                        logger.error(string)
                #printer.info(string)
                #printer.error(sorted(key_val.items()))
                #printer.error('')
                return key_val

#------------------------------------------------------

class udp_handle(BaseRequestHandler):

        def handle(self):
                string = self.get()
                key_val = proto_udp.parse_ack(string)
                key_val['addr'] = self.client_address
                logger.info(string)
                logger.info(sorted(key_val.items()))
                logger.info('')

        def get(self):
                return proto_udp.decode(self.request[0]).decode('gb18030')

#================================================================================

if __name__ == "__main__":
        server_udp = UDPServer(UDP_SERVER, udp_handle)
        server_udp.serve_forever()

