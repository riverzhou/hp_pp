#!/usr/bin/env python3

from xml.etree                  import ElementTree
from struct                     import pack, unpack
from socketserver               import ThreadingTCPServer, BaseRequestHandler
from traceback                  import print_exc

from pp_baseclass               import pp_thread, pp_sender, buff_sender
from pp_log                     import logger, printer

#============================================================================================

class base_ctrl_server(BaseRequestHandler):
        def put(self, data_tuple):
                string , proto, option  = data_tuple
                size = 12 + len(string)
                buff = pack('iii',size, proto, option)
                buff += string.encode()
                self.buff_sender.send(buff)
                printer.debug(string)

        def recv(self, sock, size) :
                buff = bytearray(size)
                view = memoryview(buff)
                try :
                        while size:
                                nbytes = sock.recv_into(view, size)
                                view   = view[nbytes:]
                                size  -= nbytes
                except KeyboardInterrupt:
                        return None
                except:
                        return None
                return buff

        def get(self):
                head = self.recv(self.request, 12)
                if not head or len(head) == 0:
                        return None
                size, proto, option = unpack('iii', head)
                data = self.recv(self.request, size - 12)
                if not data or len(data) != size - 12 :
                        return None
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
                printer.debug(sorted(key_val.items()))
                printer.debug('')
                return key_val

        def handle(self):
                logger.info('Thread %s : %s started' % (self.__class__.__name__, self.client_address))
                self.proc()
                logger.info('Thread %s : %s stoped' % (self.__class__.__name__, self.client_address))

        def proc(self): pass

#----------------------------------------------------------------------------------

class ctrl_server(base_ctrl_server):
        def make_proto_ctrl_nologin_ack(self):
                return '<XML><TYPE>NOLOGIN</TYPE></XML>' , 0 , 0

        def make_proto_ctrl_unknow_ack(self):
                return '<XML><TYPE>UNKNOW</TYPE></XML>' , 0 , 0

        def make_proto_ctrl_login_ack(self):
                return '<XML><TYPE>CT_LOGIN</TYPE><INFO>OK</INFO></XML>' , 3001 , 0

        def make_proto_ctrl_image_decode_req(self, bidid, sessionid, image):
                return ('<XML><TYPE>IMAGE_DECODE</TYPE><BIDID>%d</BIDID><SESSIONID>%s</SESSIONID><IMAGE>%s</IMAGE></XML>' % (bidid, sessionid, image)) , 3006 , 0

        def make_proto_ctrl_image_warmup_ack(self, bidid):
                return ('<XML><TYPE>IMAGE_WARMUP</TYPE><BIDID>%d</BIDID><INFO>OK</INFO></XML>' % bidid) , 3003 , 0

        def make_proto_ctrl_price_warmup_ack(self, bidid):
                return ('<XML><TYPE>PRICE_WARMUP</TYPE><BIDID>%d</BIDID><INFO>OK</INFO></XML>' % bidid) , 3005 , 0

        def make_proto_ctrl_image_shoot_ack(self, bidid):
                return ('<XML><TYPE>IMAGE_SHOOT</TYPE><BIDID>%d</BIDID><INFO>OK</INFO></XML>' % bidid) , 3009 , 0

        #------------------------------------------------------------------------

        def proc_ctrl_unknow(self, key_val): pass

        def proc_ctrl_nologin(self, key_val): pass

        def proc_ctrl_login(self, key_val): pass

        def proc_ctrl_image_decode(self, key_val): pass

        def proc_ctrl_image_warmup(self, key_val): pass

        def proc_ctrl_price_warmup(self, key_val): pass

        def proc_ctrl_image_shoot(self, key_val): pass

        def proc_ctrl_logoff(self): pass

        #------------------------------------------------------------------------

        def proc_ctrl_recv(self):
                result = self.get()

                if not result:
                        return None
                key_val = self.parse(result['data'].decode())

                if not 'TYPE' in key_val :
                        return None

                if not key_val['TYPE'] in self.func_dict:
                        self.proc_ctrl_unknow(key_val)
                        return None

                if self.login_ok != True :
                        if key_val['TYPE'] != 'CT_LOGIN' :
                                self.proc_ctrl_nologin(key_val)
                                return True

                self.func_dict[key_val['TYPE']](key_val)
                return True

        def proc(self):
                self.func_dict = {
                        'CT_LOGIN':     self.proc_ctrl_login,
                        'CT_LOGOFF':    self.proc_ctrl_logoff,
                        'IMAGE_WARMUP': self.proc_ctrl_image_warmup,
                        'PRICE_WARMUP': self.proc_ctrl_price_warmup,
                        'IMAGE_SHOOT':  self.proc_ctrl_image_shoot,
                        'IMAGE_DECODE': self.proc_ctrl_image_decode,
                        }
                self.login_ok = False
                self.buff_sender = buff_sender(self.request)
                self.buff_sender.start()
                self.buff_sender.wait_for_start()
                try:
                        while True:
                                result = self.proc_ctrl_recv()
                                if result == None : break
                except  KeyboardInterrupt:
                        pass
                except:
                        print_exc()
                finally:
                        self.proc_ctrl_logoff()
                        self.buff_sender.stop()

#----------------------------------------------------------------------------------

