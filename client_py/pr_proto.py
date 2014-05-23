#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from threading                  import Thread, Lock 
from socketserver               import ThreadingTCPServer, BaseRequestHandler
from traceback                  import print_exc
from time                       import sleep

from ct_proto                   import base_ct_server
from pp_thread                  import pp_subthread, buff_sender, price_sender
from pp_log                     import logger, printer

#==================================================================================================================

PR_SERVER = ('', 3030)

daemon_pr = price_sender()      # daemon_pr.last_price 是最新价格，全局可访问

#------------------------------------------------------------------------------------------------------------------

class proto_pr_server(base_ct_server):
        __metaclass__ = ABCMeta

        #<<刷价格>>
        def make_proto_pr_price_flush_req(self, info_val):
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

        def proc_ct_recv(self):
                try:
                        result = self.get()
                except:
                        result = None
                if not result:
                        return None
                #key_val = self.parse(result['data'].decode())
                #printer.error(result)
                #printer.error(sorted(key_val.items()))
                return True

        def handle(self):
                logger.info('Thread %s : %s started' % (self.__class__.__name__, self.client_address))
                self.buff_sender = buff_sender(self.request)
                self.buff_sender.start()
                self.buff_sender.started()
                # 注册句柄到 price_sender 线程
                global daemon_pr
                daemon_pr.reg(self)
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
                        daemon_pr.unreg(self)
                logger.info('Thread %s : %s stoped' % (self.__class__.__name__, self.client_address))

        def send(self, info_val):
                self.put(self.make_proto_pr_price_flush_req(info_val))

#================================= for test ===========================================

class pr_handler(proto_pr_server):
        pass

if __name__ == "__main__":
        ThreadingTCPServer.allow_reuse_address = True
        ThreadingTCPServer.request_queue_size  = 512
        Thread.daemon  = True
        daemon_pr.start()
        daemon_pr.started()
        server = ThreadingTCPServer(PR_SERVER, pr_handler)
        server.serve_forever()

