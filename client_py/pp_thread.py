#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from threading                  import Thread, Event, Lock, Semaphore
from pp_log                     import logger, printer
from traceback                  import print_exc
from time                       import sleep

Thread.daemon  = True

#--------------------------------------------------------------------------------------------

class pp_subthread(Thread):
        __metaclass__ = ABCMeta

        def __init__(self):
                Thread.__init__(self)
                self.stop_flag = False
                self.event_stop = Event()
                self.event_started = Event()

        def started(self):
                self.event_started.wait()

        def started_set(self):
                self.event_started.set()

        def stop(self):
                self.stop_flag = True
                self.event_stop.set()

        def wait_for_stop(self):
                self.event_stop.wait()

#--------------------------------------------------------------------------------------------

class pp_sender(pp_subthread):
        __metaclass__ = ABCMeta

        def __init__(self):
                pp_subthread.__init__(self)
                self.buff_list = []
                self.lock_buff = Lock()
                self.sem_buff = Semaphore(value=0)
                self.flag_fifo = True

        def stop(self):
                pp_subthread.stop(self)
                self.sem_buff.release()

        def put(self, buff):
                self.lock_buff.acquire()
                self.buff_list.append(buff)
                self.lock_buff.release()
                self.sem_buff.release()
                return True

        def get(self):
                if self.stop_flag == True:
                        return False
                self.sem_buff.acquire()
                if self.stop_flag == True:
                        return False
                self.lock_buff.acquire()
                if self.stop_flag == True:
                        self.lock_buff.release()
                        return False
                if len(self.buff_list) == 0 :
                        self.lock_buff.release()
                        return None
                if self.flag_fifo == True :
                        i = 0
                else :
                        i = -1
                buff = self.buff_list[i]
                del(self.buff_list[i])
                self.lock_buff.release()
                return buff

        @abstractmethod
        def proc(self, buff): pass

        def run(self):
                logger.debug('Thread %s : %s started' % (self.__class__.__name__, self.ident))
                try:
                        self.started_set()
                        while True:
                                buff = self.get()
                                if buff == False :
                                        break
                                if buff == None :
                                        continue
                                self.proc(buff)
                                sleep(0)
                except  KeyboardInterrupt:
                        pass
                except:
                        print_exc()
                logger.debug('Thread %s : %s stoped' % (self.__class__.__name__, self.ident))

#--------------------------------------------------------------------------------------------

class buff_sender(pp_sender):
        def __init__(self, sock):
                pp_sender.__init__(self)
                self.sock = sock

        def send(self, buff):
                return self.put(buff)

        def proc(self, buff):
                self.sock.sendall(buff)

#--------------------------------------------------------------------------------------------

class price_sender(pp_sender):
        def __init__(self) :
                pp_sender.__init__(self)
                self.flag_fifo = False                  # 栈模式
                self.handler_list = []
                self.lock_handler = Lock()
                self.last_price = 0                     # daemon_pr.last_price 是最新价格，全局可访问

        def proc(self, info_val):
                price = int(info_val['price'])
                if price <= self.last_price :
                        return
                self.last_price = price
                handler_list = []
                self.lock_handler.acquire()
                for handler in self.handler_list :
                        handler_list.append(handler)
                self.lock_handler.release()
                for handler in handler_list :
                        handler.send(info_val)

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

