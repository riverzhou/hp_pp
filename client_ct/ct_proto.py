#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from threading                  import Thread, Event, Condition, Lock, Event, Semaphore
from struct                     import pack, unpack
from traceback                  import print_exc
from hashlib                    import md5
from time                       import sleep
from socket                     import socket, gethostbyname, AF_INET, SOCK_STREAM, SOCK_DGRAM, SHUT_RDWR

from pp_thread                  import pp_subthread, buff_sender
from pp_log                     import logger, printer

from xml.etree                  import ElementTree

#==================================================================================================================

#------------------------------------------------------------------------------------------------------------------

class base_ct_client():
        __metaclass__ = ABCMeta

        def __init__(self):
                self.event_connected = Event()
                self.flag_connected  = False

        def wait_for_connect(self):
                self.event_connected.wait()

        def connect(self, addr):
                try:
                        self.sock = socket(AF_INET, SOCK_STREAM)
                        self.sock.connect(addr)
                except:
                        print_exc()
                        return False
                self.buff_sender = buff_sender(self.sock)
                self.buff_sender.start()
                self.buff_sender.started()
                self.event_connected.set()
                return True

        def put(self, tuple_proto):
                string , proto, option  = tuple_proto
                size = 12 + len(string)
                buff = pack('iii',size, proto, option)
                buff += string.encode()
                self.buff_sender.send(buff)
                #printer.debug(string)

        def get(self):
                try :
                        head = self.sock.recv(12)
                except:
                        head = None
                if not head or len(head) != 12 :
                        return None
                size, proto, option = unpack('iii', head)
                try:
                        data = self.sock.recv(size)
                except:
                        data = None
                if not data or len(data) == 0 :
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

#--------------------------------------------------------------------------------------------

class ctrl_ct(base_ct_client, pp_subthread):


        def __init__(self):
                base_ct_client.__init__(self)
                pp_subthread.__init__(self)
                self.event_reg = Event()

                self.func_dict =     {
                        'CT_LOGIN':     self.proc_ct_login,
                        'CT_LOGOFF':    self.proc_ct_logoff,
                        'IMAGE_WARMUP': self.proc_ct_image_warmup,
                        'PRICE_WARMUP': self.proc_ct_price_warmup,
                        'IMAGE_SHOOT':  self.proc_ct_image_shoot,
                        'IMAGE_DECODE': self.proc_ct_image_decode,
                        }

                self.cmd_dict =      {
                        'login':        self.send_ct_login,
                        'logoff':       self.send_ct_logoff,
                        'image_warmup': self.send_ct_image_warmup,
                        'price_warmup': self.send_ct_price_warmup,
                        'image_shoot':  self.send_ct_image_shoot,
                        'image_decode': self.send_ct_image_decode,
                        }

        #------------------------------------------------------------------------

        def make_proto_ct_login_req(self, bidno, passwd):
                return  ( (
                        '<XML><TYPE>CT_LOGIN</TYPE><BIDNO>%s</BIDNO><PASSWD>%s</PASSWD></XML>' 
                        % ( bidno, passwd ) ), 
                        3000 , 0 )

        def make_proto_ct_logoff_req(self):
                return 

        def make_proto_ct_image_decode_ack(self, bidid, sessionid, number):
                return  ( ( 
                        '<XML><TYPE>IMAGE_DECODE</TYPE><BIDID>%s</BIDID><SESSIONID>%s</SESSIONID><IMAGE_NUMBER>%s</IMAGE_NUMBER></XML>'
                        % ( bidid, sessionid, number ) ),
                        3007 , 0 )

        def make_proto_ct_image_warmup_req(self, bidid):
                return  ( ( 
                        '<XML><TYPE>IMAGE_WARMUP</TYPE><BIDID>%s</BIDID></XML>'
                        % bidid ),
                        3002 , 0 )

        def make_proto_ct_price_warmup_req(self, bidid):
                return  ( (
                        '<XML><TYPE>PRICE_WARMUP</TYPE><BIDID>%s</BIDID></XML>'
                        % bidid ),
                        3004 , 0 )

        def make_proto_ct_image_shoot_req(self, bidid, price):
                return  ( (
                        '<XML><TYPE>IMAGE_SHOOT</TYPE><BIDID>%s</BIDID><PRICE>%s</PRICE></XML>'
                        % ( bidid , price ) ),
                        3008 , 0 )

        #------------------------------------------------------------------------

        def send_ct_login(self, key_val):
                bidno  = key_val['bidno']
                passwd = key_val['passwd']
                self.put(self.make_proto_ct_login_req(bidno, passwd))

        def send_ct_logoff(self, key_val):
                pass

        def send_ct_image_warmup(self, key_val):
                bidid = key_val['bidid']
                self.put(self.make_proto_ct_image_warmup_req(bidid))

        def send_ct_price_warmup(self, key_val):
                bidid = key_val['bidid']
                self.put(self.make_proto_ct_price_warmup_req(bidid))

        def send_ct_image_shoot(self, key_val):
                bidid = key_val['bidid']
                price = key_val['price']
                self.put(self.make_proto_ct_image_shoot_req(bidid, price))

        def send_ct_image_decode(self, key_val):
                bidid      = key_val['bidid']
                #sessionid = key_val['sessionid']
                sessionid  = self.sessionid
                number     = key_val['number']
                self.put(self.make_proto_ct_image_decode_ack(bidid, sessionid, number))

        #------------------------------------------------------------------------

        def proc_ct_login(self, key_val):
                pass

        def proc_ct_image_decode(self, key_val):
                info_val = {}
                info_val['cmd']       = 'req'
                info_val['bidid']     = key_val['BIDID']
                info_val['sessionid'] = key_val['SESSIONID']
                info_val['image']     = key_val['IMAGE']
                self.sessionid        = key_val['SESSIONID']
                self.handle.update_image_decode(info_val)

        def proc_ct_image_warmup(self, key_val):
                info_val = {}
                info_val['cmd']   = 'ack'
                info_val['bidid'] = key_val['BIDID']
                self.handle.update_image_warmup(info_val)

        def proc_ct_price_warmup(self, key_val):
                info_val = {}
                info_val['cmd']   = 'ack'
                info_val['bidid'] = bidid = key_val['BIDID']
                self.handle.update_price_warmup(info_val)

        def proc_ct_image_shoot(self, key_val):
                info_val = {}
                info_val['cmd']   = 'ack'
                info_val['bidid'] = bidid = key_val['BIDID']
                self.handle.update_image_shoot(info_val)

        def proc_ct_logoff(self):
                pass

        #------------------------------------------------------------------------

        def reg(self, handler):
                self.handler = handler
                self.event_reg.set()

        def wait_for_reg(self):
                self.event_reg.wait()

        def send(self, key_val):
                self.cmd_dict[key_val['cmd']](key_val)

        def proc_ct_recv(self):
                result = self.get()
                if not result:
                        return None
                key_val = self.parse(result['data'].decode())
                self.func_dict[key_val['TYPE']](key_val)
                return True

        def run(self):
                logger.info('Thread %s started' % (self.__class__.__name__))
                self.started_set()
                self.wait_for_reg()
                self.wait_for_connect()
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
                logger.info('Thread %s stoped' % (self.__class__.__name__))

#================================= for test ===========================================


if __name__ == "__main__":
        pass

