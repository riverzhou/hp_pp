#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from threading                  import Thread, Lock 
from socketserver               import ThreadingTCPServer, BaseRequestHandler
from traceback                  import print_exc
from time                       import sleep

from ct_proto                   import base_ct_server
from pp_thread                  import pp_subthread, buff_sender, price_sender
from pp_log                     import logger, ct_printer as printer

#==================================================================================================================

PR_SERVER = ('', 3030)

#------------------------------------------------------------------------------------------------------------------

class proto_pr_server(base_ct_server):
        __metaclass__ = ABCMeta

        #<<刷价格>>
        def make_proto_pr_price_flush_req(self, price):
                return ('<XML><TYPE>PRICE_FLUSH</TYPE><PRICE>%d</PRICE></XML>' % price) , 0 , 0

        def proc_ct_recv(self):
                result = self.get()
                if not result:
                        return None
                #key_val = self.parse(result['data'].decode())
                printer.error(result)
                #printer.error(key_val)
                return True

        def handle(self):
                logger.debug('Thread %s : %s started' % (self.__class__.__name__, self.client_address))
                self.buff_sender = self.request
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
                logger.debug('Thread %s : %s stoped' % (self.__class__.__name__, self.client_address))

        def send(self, price):
                self.put(self.make_proto_pr_price_flush_req(price))

#================================= for test ===========================================

class pr_handler(proto_pr_server):
        pass

if __name__ == "__main__":
        ThreadingTCPServer.allow_reuse_address = True
        Thread.daemon  = True
        global daemon_pr
        daemon_pr = price_sender()
        daemon_pr.start()
        daemon_pr.started()
        server = ThreadingTCPServer(PR_SERVER, pr_handler)
        server.serve_forever()

