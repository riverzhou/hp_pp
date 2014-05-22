#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from threading                  import Thread, Event, Condition, Lock, Event, Semaphore
from struct                     import pack, unpack
from socketserver               import ThreadingTCPServer, BaseRequestHandler
from traceback                  import print_exc
from hashlib                    import md5
from time                       import sleep

from pp_thread                  import pp_subthread, buff_sender
from pp_log                     import logger, ct_printer as printer

from xml.etree                  import ElementTree

#==================================================================================================================

CT_SERVER = ('', 3000)

#------------------------------------------------------------------------------------------------------------------

class base_ct_server(BaseRequestHandler):
        __metaclass__ = ABCMeta

        def put(self, tuple_proto):
                string , proto, option  = tuple_proto
                size = 12 + len(string)
                buff = pack('iii',size, proto, option)
                buff += string.encode()
                self.buff_sender.send(buff)
                #printer.debug(string)

        def get(self):
                head = self.request.recv(12)
                if not head or len(head) != 12:
                        return
                size, proto, option = unpack('iii', head)
                data = self.request.recv(size)
                if not head:
                        return
                result = {}
                result['size'] = size
                result['proto'] = proto
                result['option'] = option
                result['data'] = data
                printer.debug(data.decode())
                return result

        def parse(self, xml_string):
                key_val = {}
                try:
                        root = ElementTree.fromstring(xml_string)
                        for child in root:
                                key_val[child.tag] = child.text
                except:
                        printer.error(xml_string)
                        print_exc()
                printer.debug(key_val)
                printer.debug('')
                return key_val

#--------------------------------------------------------------------------------------------

class proto_ct_server(base_ct_server):
        __metaclass__ = ABCMeta

        #<<登录>>
        def make_proto_ct_nologin_ack(self):
                return '<XML><TYPE>NOLOGIN</TYPE></XML>' , 0 , 0

        def make_proto_ct_unknow_ack(self):
                return '<XML><TYPE>UNKNOW</TYPE></XML>' , 0 , 0

        def make_proto_ct_login_ack(self):
                return '<XML><TYPE>CT_LOGIN</TYPE><INFO>OK</INFO></XML>' , 3001 , 0

        #<<模式1>>
        def make_proto_ct_image_decode_req(self, bidid, sessionid, image):
                return ('<XML><TYPE>IMAGE_DECODE</TYPE><BIDID>%d</BIDID><SESSIONID>%s</SESSIONID><IMAGE>%s</IMAGE></XML>' % (bidid, sessionid, image)) , 3006 , 0

        def make_proto_ct_image_warmup_ack(self, bidid):
                return ('<XML><TYPE>IMAGE_WARMUP</TYPE><BIDID>%d</BIDID><INFO>OK</INFO></XML>' % bidid) , 3003 , 0

        def make_proto_ct_price_warmup_ack(self, bidid):
                return ('<XML><TYPE>PRICE_WARMUP</TYPE><BIDID>%d</BIDID><INFO>OK</INFO></XML>' % bidid) , 3005 , 0

        def make_proto_ct_image_shoot_ack(self, bidid):
                return ('<XML><TYPE>IMAGE_SHOOT</TYPE><BIDID>%d</BIDID><INFO>OK</INFO></XML>' % bidid) , 3009 , 0

        #<<模式2>>
        def make_proto_ct_image_pool_ack(self, bidid):
                return ('<XML><TYPE>IMAGE_POOL</TYPE><BIDID>%d</BIDID><INFO>OK</INFO></XML>' % bidid) , 3023 , 0

        def make_proto_ct_pool_decode_req(self, bidid, sessionid, image):
                return ('<XML><TYPE>POOL_DECODE</TYPE><BIDID>%d</BIDID><SESSIONID>%s</SESSIONID><IMAGE>%s</IMAGE></XML>' % (bidid, sessionid, image)) , 3024 , 0

        def make_proto_ct_price_shoot_ack(self, bidid):
                return ('<XML><TYPE>PRICE_SHOOT</TYPE><BIDID>%d</BIDID><INFO>OK</INFO></XML>' % bidid) , 3021 , 0

        #------------------------------------------------------------------------

        #<<继承后重写>>
        @abstractmethod
        def proc_ct_unknow(self, key_val): pass

        @abstractmethod
        def proc_ct_nologin(self, key_val): pass

        @abstractmethod
        def proc_ct_login(self, key_val): pass

        @abstractmethod
        def proc_ct_image_decode(self, key_val): pass

        @abstractmethod
        def proc_ct_image_warmup(self, key_val): pass

        @abstractmethod
        def proc_ct_price_warmup(self, key_val): pass

        @abstractmethod
        def proc_ct_image_shoot(self, key_val): pass

        @abstractmethod
        def proc_ct_image_pool(self, key_val): pass

        @abstractmethod
        def proc_ct_pool_decode(self, key_val): pass

        @abstractmethod
        def proc_ct_price_shoot(self, key_val): pass

        @abstractmethod
        def proc_ct_logoff(self): pass

        #------------------------------------------------------------------------

        def proc_ct_recv(self):
                result = self.get()
                if not result:
                        return None
                key_val = self.parse(result['data'].decode())

                if not key_val['TYPE'] in self.func_dict:
                        return self.proc_ct_unknow(key_val)

                if self.login_ok != True :
                        if key_val['TYPE'] != 'CT_LOGIN' :
                                return self.proc_ct_nologin(key_val)

                self.func_dict[key_val['TYPE']](key_val)
                return True

        def handle(self):
                logger.debug('Thread %s : %s started' % (self.__class__.__name__, self.client_address))
                self.func_dict = {
                        'CT_LOGIN':     self.proc_ct_login,
                        'IMAGE_WARMUP': self.proc_ct_image_warmup,
                        'PRICE_WARMUP': self.proc_ct_price_warmup,
                        'IMAGE_SHOOT':  self.proc_ct_image_shoot,
                        'IMAGE_DECODE': self.proc_ct_image_decode,
                        'IMAGE_POOL' :  self.proc_ct_image_pool,
                        'POOL_DECODE':  self.proc_ct_pool_decode,
                        'PRICE_SHOOT':  self.proc_ct_price_shoot,
                        }
                self.login_ok = False
                self.buff_sender = buff_sender(self.request)
                self.buff_sender.start()
                self.buff_sender.started()
                try:
                        while True:
                                result = self.proc_ct_recv()
                                if result == None :
                                        break
                                sleep(0)
                except  KeyboardInterrupt:
                        pass
                except:
                        print_exc()
                finally:
                        self.proc_ct_logoff()
                        self.buff_sender.stop()
                logger.debug('Thread %s : %s stoped' % (self.__class__.__name__, self.client_address))

#================================= for test ===========================================

class ct_handler(proto_ct_server):
        def proc_ct_unknow(self, key_val):
                self.put(self.make_proto_ct_unknow_ack())
                return True

        def proc_ct_nologin(self, key_val):
                self.put(self.make_proto_ct_nologin_ack())
                return True

        def proc_ct_login(self, key_val):
                self.bidno = key_val['BIDNO']
                self.passwd = key_val['PASSWD']

                self.login_ok = True
                self.put(self.make_proto_ct_login_ack())
                return True

        def proc_ct_image_decode(self, key_val):
                self.put(self.make_proto_ct_image_decode_req(1, 'CCCCCCC', 'xxxxxxxx'))
                return True

        def proc_ct_image_warmup(self, key_val):
                self.put(self.make_proto_ct_image_warmup_ack(1))
                return True

        def proc_ct_price_warmup(self, key_val):
                self.put(self.make_proto_ct_price_warmup_ack(1))
                return True

        def proc_ct_image_shoot(self, key_val):
                self.put(self.make_proto_ct_image_shoot_ack(1))
                return True

        def proc_ct_image_pool(self, key_val):
                self.put(self.make_proto_ct_image_pool_ack(1))
                return True

        def proc_ct_pool_decode(self, key_val):
                self.put(self.make_proto_ct_pool_decode_req(1, 'CCCCCCC', 'xxxxxxxx'))
                return True

        def proc_ct_price_shoot(self, key_val):
                self.put(self.make_proto_ct_price_shoot_ack(1))
                return True

        def proc_ct_logoff(self):
                return True

if __name__ == "__main__":
        ThreadingTCPServer.allow_reuse_address = True
        ThreadingTCPServer.request_queue_size  = 512
        Thread.daemon  = True
        server = ThreadingTCPServer(CT_SERVER, ct_handler)
        server.serve_forever()

