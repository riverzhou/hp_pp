#!/usr/bin/env python3



from abc                        import ABCMeta, abstractmethod
from threading                  import Thread
from multiprocessing            import Process, Event, Condition, Lock, Event
from struct                     import pack, unpack
from socket                     import socket
from traceback                  import print_exc
from time                       import time, localtime, strftime
from time                       import sleep
from socket                     import socket, gethostbyname, AF_INET, SOCK_STREAM, SOCK_DGRAM
from xml.etree                  import ElementTree
import random, string

# <proto_head>
#typedef struct {       
#        int packet_len;
#        int proto_id;
#        int option;
#} PROTO_HEAD;

#<client -> server>
#<<登录请求>>
proto_ct_login_req              = '<XML><TYPE>CT_LOGIN</TYPE><BIDNO>88888888</BIDNO><PASSWD>4444</PASSWD></XML>'

#<<模式1协议>>
proto_ct_image_warmup_req       = '<XML><TYPE>IMAGE_WARMUP</TYPE><BIDID>1</BIDID></XML>'
proto_ct_price_warmup_req       = '<XML><TYPE>PRICE_WARMUP</TYPE><BIDID>1</BIDID></XML>'
proto_ct_image_shoot_req        = '<XML><TYPE>IMAGE_SHOOT</TYPE><BIDID>1</BIDID><PRICE>74000</PRICE></XML>'
proto_ct_image_decode_ack       = '<XML><TYPE>IMAGE_DECODE</TYPE><BIDID>1</BIDID><SESSIONID>CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC</SESSIONID><IMAGE_NUMBER>666666</IMAGE_NUMBER></XML>'

#<<模式2协议>>
#proto_ct_price_warmup_req      复用模式1的协议
proto_ct_price_shoot_req        = '<XML><TYPE>PRICE_SHOOT</TYPE><BIDID>1</BIDID><PRICE>74000</PRICE></XML>'
proto_ct_image_pool_req         = '<XML><TYPE>IMAGE_POOL</TYPE><BIDID>1</BIDID><PRICE>70000</PRICE></XML>'
proto_ct_pool_decode_ack        = '<XML><TYPE>POOL_DECODE</TYPE><BIDID>1</BIDID><SESSIONID>CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC</SESSIONID><IMAGE_NUMBER>666666</IMAGE_NUMBER></XML>'

#<<独立线程>>
proto_ct_price_flush_ack        = '<XML><TYPE>PRICE_FLUSH</TYPE><INFO>OK</INFO></XML>'

#<server -> client>
#<<登录请求>>
proto_ct_login_ack              = '<XML><TYPE>CT_LOGIN</TYPE><INFO>OK</INFO></XML>'

#<<模式1协议>>
proto_ct_image_decode_req       = '<XML><TYPE>IMAGE_DECODE</TYPE><BIDID>1</BIDID><SESSIONID>CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC</SESSIONID><IMAGE>base64_XXXXXXXX</IMAGE></XML>'
proto_ct_image_warmup_ack       = '<XML><TYPE>IMAGE_WARMUP</TYPE><BIDID>1</BIDID><INFO>OK</INFO></XML>'
proto_ct_price_warmup_ack       = '<XML><TYPE>PRICE_WARMUP</TYPE><BIDID>1</BIDID><INFO>OK</INFO></XML>'
proto_ct_image_shoot_ack        = '<XML><TYPE>IMAGE_SHOOT</TYPE><BIDID>1</BIDID><INFO>OK</INFO></XML>'

#<<模式2协议>>
#proto_ct_price_warmup_ack      复用模式1的协议
#proto_ct_image_pool_ack        合并到proto_ct_pool_decode_req协议中，不独立处理
proto_ct_pool_decode_req        = '<XML><TYPE>POOL_DECODE</TYPE><BIDID>1</BIDID><SESSIONID>CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC</SESSIONID><IMAGE>base64_XXXXXXXX</IMAGE></XML>'
proto_ct_price_shoot_ack        = '<XML><TYPE>PRICE_SHOOT</TYPE><BIDID>1</BIDID><INFO>OK</INFO></XML>'

#<<独立线程>>
proto_ct_price_flush_req        = '<XML><TYPE>PRICE_FLUSH</TYPE><PRICE>72000</PRICE></XML>'


CT_SERVER = ( '127.0.0.1', 3000)


class ct_client():
        def __init__(self):
                global CT_SERVER
                self.sock = socket(AF_INET, SOCK_STREAM)
                self.sock.connect(CT_SERVER)

        def proto_ct_login_req(self):
                return '<XML><TYPE>CT_LOGIN</TYPE><BIDNO>88888888</BIDNO><PASSWD>4444</PASSWD></XML>'

        def proto_ct_image_warmup_req(self):
                return '<XML><TYPE>IMAGE_WARMUP</TYPE><BIDID>1</BIDID></XML>'

        def proto_ct_price_warmup_req(self):
                return '<XML><TYPE>PRICE_WARMUP</TYPE><BIDID>1</BIDID></XML>'

        def proto_ct_image_shoot_req(self):
                return '<XML><TYPE>IMAGE_SHOOT</TYPE><BIDID>1</BIDID><PRICE>74000</PRICE></XML>'

        def proto_ct_image_decode_ack(self):
                return '<XML><TYPE>IMAGE_DECODE</TYPE><BIDID>1</BIDID><SESSIONID>CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC</SESSIONID><IMAGE_NUMBER>666666</IMAGE_NUMBER></XML>'

        def proto_ct_price_shoot_req(self):
                return '<XML><TYPE>PRICE_SHOOT</TYPE><BIDID>1</BIDID><PRICE>74000</PRICE></XML>'

        def proto_ct_image_pool_req(self):
                return '<XML><TYPE>IMAGE_POOL</TYPE><BIDID>1</BIDID><PRICE>70000</PRICE></XML>'

        def proto_ct_pool_decode_ack(self):
                return '<XML><TYPE>POOL_DECODE</TYPE><BIDID>1</BIDID><SESSIONID>CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC</SESSIONID><IMAGE_NUMBER>666666</IMAGE_NUMBER></XML>'

        def proto_ct_price_flush_ack(self):
                return '<XML><TYPE>PRICE_FLUSH</TYPE><INFO>OK</INFO></XML>'

        #-----------------------------------------------------------------------------------------------------------

        def send_ct_login_req(self):
                self.push(self.proto_ct_login_req())

        def send_ct_image_warmup_req(self):
                self.push(self.proto_ct_image_warmup_req())

        def send_ct_price_warmup_req(self):
                self.push(self.proto_ct_price_warmup_req())

        def send_ct_image_shoot_req(self):
                self.push(self.proto_ct_image_shoot_req())

        def send_ct_image_decode_ack(self):
                self.push(self.proto_ct_image_decode_ack())

        def send_ct_price_shoot_req(self):
                self.push(self.proto_ct_price_shoot_req())

        def send_ct_image_pool_req(self):
                self.push(self.proto_ct_image_pool_req())

        def send_ct_pool_decode_ack(self):
                self.push(self.proto_ct_pool_decode_ack())

        def send_ct_price_flush_ack(self):
                self.push(self.proto_ct_price_flush_ack())

        def send(self, buff):
                self.sock.send(buff)
                print(buff)
                print()

        def recv(self):
                head = self.sock.recv(12)
                if not head:
                        return 
                size, proto, option = unpack('iii', head)
                data = self.sock.recv(size)
                result = {}
                result['size'] = size
                result['proto'] = proto
                result['option'] = option
                result['data'] = data
                print(data)
                return result

        def push(self, string):
                size = len(string) + 12
                buff = pack('iii', size, 0, 0)
                buff += string.encode()
                self.send(buff)
                result = self.recv()
                if not result:
                        return
                key_val = self.parse(result['data'])
                #self.sock.shutdown()
                #self.sock.close()
                print(key_val)
                print()
                return key_val

        def parse(self, buff):
                xml_string = buff.decode()
                key_val = {}
                try:
                        root = ElementTree.fromstring(xml_string)
                        for child in root:
                                key_val[child.tag] = child.text
                except :
                        print(xml_string)
                return key_val

if __name__ == "__main__":
        ct = ct_client()

        ct.send_ct_login_req()
        sleep(1)

        ct.send_ct_image_warmup_req()
        sleep(1)

        ct.send_ct_image_warmup_req()
        sleep(1)

        ct.send_ct_price_warmup_req()
        sleep(1)

        ct.send_ct_image_shoot_req()
        sleep(1)

        ct.send_ct_image_decode_ack()
        sleep(1)

        ct.send_ct_price_shoot_req()
        sleep(1)

        ct.send_ct_image_pool_req()
        sleep(1)

        ct.send_ct_pool_decode_ack()
        sleep(1)

        ct.send_ct_price_flush_ack()
        sleep(1)

