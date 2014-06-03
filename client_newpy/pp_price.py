#!/usr/bin/env python3

#from socketserver               import ThreadingTCPServer, BaseRequestHandler
from threading                  import Lock
from traceback                  import print_exc

from pp_baseclass               import pp_thread, pp_sender, buff_sender
from pp_ctrl                    import base_ctrl_server
from pp_log                     import logger, printer

#==================================================================================

class price_sender(pp_sender):
        def __init__(self, info = '') :
                pp_sender.__init__(self, info, lifo = True)
                self.handler_list = []
                self.lock_handler = Lock()
                self.last_price = 0

        def proc(self, info_val):
                price = int(info_val['price'])
                if price <= self.last_price :
                        return True
                self.last_price = price
                handler_list = []
                self.lock_handler.acquire()
                for handler in self.handler_list :
                        handler_list.append(handler)
                self.lock_handler.release()
                for handler in handler_list :
                        handler.send(info_val)
                return True

        def send(self, info_val):
                price = int(info_val['price'])
                last_price = self.last_price
                if price <= last_price :
                        return
                return self.put(info_val)

        def reg(self, handler):
                self.lock_handler.acquire()
                if not handler in self.handler_list :
                        self.handler_list.append(handler)
                self.lock_handler.release()

        def unreg(self, handler):
                self.lock_handler.acquire()
                for i in range(len(self.handler_list)) :
                        if self.handler_list[i] == handler :
                                del(self.handler_list[i])
                                break
                self.lock_handler.release()

#----------------------------------------------------------------------------------

class price_server(base_ctrl_server):
        def make_proto_price_flush_req(self, info_val):
                return ( ( (
                        '<XML>'+
                        '<TYPE>PRICE_FLUSH</TYPE>'+
                        '<PRICE>%s</PRICE>'+
                        '<NUMBER>%s</NUMBER>'+
                        '<SYSTIME>%s</SYSTIME>'+
                        '<LOWTIME>%s</LOWTIME>'+
                        '</XML>'
                        ) % (
                        info_val['price'],
                        info_val['number'],
                        info_val['systime'],
                        info_val['lowtime']
                        ) ) ,
                        3030 , 0 )

        def proc_ctrl_recv(self):
                try:
                        result = self.get()
                except:
                        return None
                if not result:
                        return None
                return result

        def proc(self):
                self.buff_sender = buff_sender(self.request)
                self.buff_sender.start()
                self.buff_sender.wait_for_start()
                global daemon_pr
                daemon_pr.reg(self)

                try:
                        while True:
                                result = self.proc_ctrl_recv()
                                if result == None : break
                except  KeyboardInterrupt:
                        pass
                except:
                        print_exc()
                finally:
                        daemon_pr.unreg(self)

        def send(self, info_val):
                self.put(self.make_proto_price_flush_req(info_val))

#----------------------------------------------------------------------------------

