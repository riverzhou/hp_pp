#!/usr/bin/env python3

from threading              import Thread, Event, Lock, Semaphore
from queue                  import Queue, LifoQueue
from traceback              import print_exc

from pp_log                 import printer

#============================================================================================

class pp_thread(Thread):
        default_start_timeout = 5

        def __init__(self, info = ''):
                super().__init__()
                self.flag_stop     = False
                self.event_stop    = Event()
                self.event_stopped = Event()
                self.event_started = Event()
                self.thread_info   = info
                self.setDaemon(True)

        def wait_for_start(self, timeout = None):
                if timeout == None:
                        self.event_started.wait()
                else:
                        try:
                                int(timeout)
                        except  KeyboardInterrupt:
                                pass
                        except:
                                printer.critical(format_exc())
                                self.event_started.wait(self.default_start_timeout)
                        else:
                                self.event_started.wait(timeout)

        def wait_for_stop(self):
                try:
                        self.event_stopped.wait()
                except  KeyboardInterrupt:
                        pass
                except:
                        printer.critical(format_exc())

        def stop(self):
                self.flag_stop = True
                self.event_stop.set()

        def run(self):
                #if self.thread_info != None : print('Thread %s : Id %s : %s : started' % (self.__class__.__name__, self.ident, self.thread_info))
                self.event_started.set()
                self.main()
                self.event_stopped.set()
                #if self.thread_info != None : print('Thread %s : Id %s : %s : stoped' % (self.__class__.__name__, self.ident, self.thread_info))

        def main(self): pass

#--------------------------------------------------------------------------------------------

