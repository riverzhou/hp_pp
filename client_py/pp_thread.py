#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from threading                  import Thread, Event, Condition, Lock, Event, Semaphore


Thread.daemon  = True


class pp_subthread(Thread):
        __metaclass__ = ABCMeta

        def __init__(self):
                Thread.__init__(self)
                self.stop = False
                self.event_stop = Event()
                self.event_started = Event()

        def started(self):
                self.event_started.wait()

        def started_set(self):
                self.event_started.set()

        def stop(self):
                self.stop = True
                self.event_stop.set()

        def wait_for_stop(self):
                self.event_stop_wait()


#--------------------------------------------------------------------------------------------

class buff_sender(pp_subthread):
        def __init__(self, sock) :
                pp_subthread.__init__(self)
                self.sock = sock
                self.buff_list = []
                self.lock_buff = Lock()
                self.sem_buff = Semaphore()

        def run(self):
                try:
                        self.started_set()
                        while True:
                                if self.stop == True:
                                        return
                                self.sem_buff.acquire()
                                if self.stop == True:
                                        return
                                self.lock_buff.acquire()
                                if self.stop == True:
                                        self.lock_buff.release()
                                        return
                                if len(self.buff_list) == 0 :
                                        self.lock_buff.release()
                                        continue
                                buff = self.buff_list[0]
                                del(self.buff_list[0])
                                self.lock_buff.release()
                                self.sock.send(buff)
                except:
                        pass

        def send(self, buff):
                self.lock_buff.acquire()
                self.buff_list.append(buff)
                self.lock_buff.release()
                self.sem_buff.release()

        def stop(self):
                pp_subthread.stop(self)
                self.sem_buff.release()
                self.lock_buff.release()

