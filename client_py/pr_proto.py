#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from threading                  import Thread, Event, Condition, Lock, Event, Semaphore
from struct                     import pack, unpack
from socketserver               import ThreadingTCPServer, BaseRequestHandler
from traceback                  import print_exc
from time                       import time, localtime, strftime
from time                       import sleep
from socket                     import socket, gethostbyname, AF_INET, SOCK_STREAM, SOCK_DGRAM
import random, string

from pp_thread                  import pp_subthread, buff_sender
from pp_log                     import logger, ct_printer as printer

from xml.etree                  import ElementTree

ThreadingTCPServer.allow_reuse_address = True
Thread.daemon  = True

#----------------------------

PR_SERVER = ('', 3030)

#--------------------------------------------------------------------------------------------

class proto_pr_server(BaseRequestHandler):

        #<<刷价格>>
        def make_proto_pr_price_flush_req(self, price):
                return ('<XML><TYPE>PRICE_FLUSH</TYPE><PRICE>%d</PRICE></XML>' % price)

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
                try:
                        while True:
                                result = self.proc_ct_recv()
                                if result == None :
                                        break
                                sleep(0)
                except:
                        print_exc()
                finally:
                        pass
                logger.debug('Thread %s : %s stoped' % (self.__class__.__name__, self.client_address))

        def send(self, price):
                self.put(self.make_proto_pr_price_flush_req(price))

#================================= for test ===========================================

class pr_handler(proto_pr_server):

if __name__ == "__main__":
        server = ThreadingTCPServer(PR_SERVER, pr_handler)
        server.serve_forever()

