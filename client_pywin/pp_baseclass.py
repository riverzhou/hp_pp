#!/usr/bin/env python3

from threading          import Thread, Event, Lock, Semaphore
from queue              import Queue, LifoQueue
from traceback          import print_exc

from pp_log             import logger

#============================================================================================

class pp_thread(Thread):
        def __init__(self, info = ''):
                Thread.__init__(self)
                self.flag_stop     = False
                self.event_stop    = Event()
                self.event_started = Event()
                self.thread_info   = info
                self.setDaemon(True)

        def wait_for_start(self):
                self.event_started.wait()

        def stop(self):
                self.flag_stop = True
                self.event_stop.set()

        def run(self):
                if info != None : logger.debug('Thread %s : Id %s : %s : started' % (self.__class__.__name__, self.ident, self.thread_info))
                self.event_started.set()
                try:
                        self.main()
                except KeyboardInterrupt:
                        pass
                if info != None : logger.debug('Thread %s : Id %s : %s : stoped' % (self.__class__.__name__, self.ident, self.thread_info))

        def main(self): pass

#--------------------------------------------------------------------------------------------

class pp_sender(pp_thread):
        def __init__(self, info = '', lifo = False):
                pp_thread.__init__(self, info)
                self.queue = Queue() if not lifo else LifoQueue()

        def put(self, buff):
                self.queue.put(buff)

        def stop(self):
                pp_thread.stop(self)
                self.put(None)

        def get(self):
                try:
                        return self.queue.get()
                except KeyboardInterrupt:
                        raise KeyboardInterrupt

        def main(self):
                while True:
                        buff = self.get()
                        if self.flag_stop  == True or not buff  : break
                        if self.proc(buff) == True              : self.queue.task_done()
                        if self.flag_stop  == True              : break

        def proc(self, buff): pass

#--------------------------------------------------------------------------------------------

class buff_sender(pp_sender):
        def __init__(self, sock, info):
                pp_sender.__init__(self, info)
                self.sock = sock

        def send(self, buff):
                self.put(buff)

        def proc(self, buff):
                try:
                        self.sock.sendall(buff)
                        return True
                except KeyboardInterrupt:
                        raise KeyboardInterrupt
                except:
                        print_exc()
                        return False

#--------------------------------------------------------------------------------------------

