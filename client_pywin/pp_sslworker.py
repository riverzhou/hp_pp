#!/usr/bin/env python3

#==========================================================

from pp_log             import logger, printer
from threading          import Thread, Event, Lock, Semaphore
from queue              import Queue, LifoQueue
from traceback          import print_exc

from pp_baseclass       import pp_thread, pp_sender
from pp_sslproto        import *

#==========================================================


class ssl_worker(pp_thread):
        def __init__(self, info = ''):
                pp_thread.__init__(self, info)
                self.event_proc = Event()
                self.arg        = None

        def main(self):
                self.event_proc.wait()
                self.do_proc(self.arg)

        def proc(self, arg):
                self.arg = arg
                self.event_proc.set()

        def do_proc(self, arg): pass

        def pyget(self, host, req, headers = {}, timeout = None):
                while True:
                        handler = HTTPSConnection(host, timeout = timeout)
                        handler._http_vsn = 10
                        handler._http_vsn_str = 'HTTP/1.0'
                        try:
                                handler.connect()
                        except (sock_timeout, TimeoutError):
                                handler.close()
                                continue
                        except:
                                print_exc()
                                continue
                        break
                #--------------------------------------------------------
                try:
                        handler.request('GET', req, headers = headers)
                except:
                        handler.close()
                        print_exc()
                        return None
                try:
                        ack  = handler.getresponse()
                        body = ack.read()
                except:
                        handler.close()
                        print_exc()
                        return None
                #--------------------------------------------------------
                handler.close()

                key_val = {}
                key_val['body']    = body
                key_val['head']    = str(ack.msg)
                key_val['status']  = ack.status

                return key_val


class ssl_login_worker(ssl_worker):
        def do_proc(self, arg):
                cmd, key_val, callback = arg
                if cmd == 'login' :
                        return self.do_login(key_val, callback )
                logger.debug('ssl_login_worker cmd : %s unknow' % cmd)

        def do_login(self, key_val, callback):
                print(sorted(key_val.items()))



class ssl_toubiao_worker(ssl_login_worker):
        def do_proc(self, arg):
                cmd, key_val, callback = arg
                if cmd == 'price' :
                        return self.do_price(key_val, callback )
                if cmd == 'image' :
                        return self.do_image(key_val, callback )
                logger.debug('ssl_toubiao_worker cmd : %s unknow' % cmd)

        def do_image(self, key_val, callback):
                print(sorted(key_val.items()))

        def do_price(self, key_val, callback):
                print(sorted(key_val.items()))


#==========================================================


class ssl_sender(pp_sender):
        def send(self, cmd, key_val, callback):
                self.put((cmd, key_val, callback))


class ssl_login_sender(ssl_sender):
        def proc(self, arg):
                worker = ssl_login_worker('ssl_login_worker')
                worker.start()
                worker.wait_for_start()
                worker.proc(arg)


class ssl_toubiao_sender(ssl_sender):
        def proc(self, arg):
                worker = ssl_toubiao_worker('ssl_toubiao_worker')
                worker.start()
                worker.wait_for_start()
                worker.proc(arg)


#==========================================================

proc_ssl_login   = ssl_login_sender()
proc_ssl_login.start()
proc_ssl_login.wait_for_start()

proc_ssl_toubiao = ssl_toubiao_sender()
proc_ssl_toubiao.start()
proc_ssl_toubiao.wait_for_start()

