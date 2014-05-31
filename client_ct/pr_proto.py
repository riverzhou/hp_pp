#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from threading                  import Thread, Lock, Event
from socketserver               import ThreadingTCPServer, BaseRequestHandler
from traceback                  import print_exc
from time                       import sleep

from ct_proto                   import base_ct_client
from pp_thread                  import pp_subthread
from pp_log                     import logger, printer

#==================================================================================================================

#------------------------------------------------------------------------------------------------------------------

class ctrl_pr(base_ct_client, pp_subthread):
        def __init__(self):
                base_ct_client.__init__(self)
                pp_subthread.__init__(self)
                self.event_reg = Event()

        def run(self):
                logger.info('Thread %s : started' % (self.__class__.__name__))
                self.started_set()
                self.wait_for_reg()
                self.wait_for_connect()
                try:
                        while True:
                                result = self.get()
                                if result == None :
                                        break
                                key_val = self.parse(result['data'])
                                self.proc(key_val)
                                sleep(0)
                except  KeyboardInterrupt:
                        pass
                except:
                        print_exc()
                logger.info('Thread %s : stoped' % (self.__class__.__name__))

        def reg(self, handler):
                self.handler = handler
                self.event_reg.set()

        def wait_for_reg(self):
                self.event_reg.wait()

        def proc(self, key_val):
                self.handler.update_info(key_val)

#================================= for test ===========================================

class ctrl_pr(ctrl_pr):
        def proc(self, key_val):
                print(sorted(key_val.items()))

if __name__ == "__main__":
        daemon_pr = ctrl_pr()
        daemon_pr.start()
        daemon_pr.started()
        daemon_pr.reg(None)
        daemon_pr.join()

