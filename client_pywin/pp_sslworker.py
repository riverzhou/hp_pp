#!/usr/bin/env python3

#==========================================================

from pp_log             import logger, printer
from threading          import Thread, Event, Lock, Semaphore
from queue              import Queue, LifoQueue
from traceback          import print_exc

from http.client        import HTTPSConnection, HTTPConnection
from socket             import timeout as sock_timeout
#from time              import strftime, localtime, time

from pp_baseclass       import pp_thread, pp_sender
from pp_server          import server_dict
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
                global    server_dict
                key_val, callback = arg

                group     = key_val['group']
                host_ip   = server_dict[group]['login']['ip']
                host_name = server_dict[group]['login']['name']

                proto     = proto_ssl_login(key_val)
                req       = proto.make_login_req()
                head      = proto.make_ssl_head(host_name)
                info_val  = self.pyget(host_ip, req, head)
                #logger.debug(sorted(info_val.items()))

                if info_val['status'] != 200 :
                        logger.error('ack status error!!!')
                        logger.error(sorted(info_val.items()))
                        #logger.error(info_val['body'].decode())
                        return

                ack_sid   = proto.get_sid_from_head(info_val['head'])
                ack_val   = proto.parse_login_ack(info_val['body'])
                #ack_val['sid'] = ack_sid
                printer.debug(sorted(ack_val.items()))
                #logger.debug(sorted(ack_val.items()))

                if callback != None : callback(ack_val)
                return ack_val

class ssl_image_worker(ssl_worker):
        def do_proc(self, arg):
                global    server_dict
                key_val, callback = arg

                price     = key_val['image_price']
                group     = key_val['group']
                host_ip   = server_dict[group]['toubiao']['ip']
                host_name = server_dict[group]['toubiao']['name']

                proto     = proto_ssl_image(key_val)
                req       = proto.make_image_req(price)
                head      = proto.make_ssl_head(host_name)
                info_val  = self.pyget(host_ip, req, head)
                #logger.debug(sorted(info_val.items()))

                if info_val['status'] != 200 :
                        logger.error('ack status error!!!')
                        logger.error(sorted(info_val.items()))
                        #logger.error(info_val['body'].decode())
                        return

                ack_sid   = proto.get_sid_from_head(info_val['head'])
                ack_val   = proto.parse_image_ack(info_val['body'])
                ack_val['sid']   = ack_sid
                ack_val['price'] = price
                printer.debug(sorted(ack_val.items()))
                #logger.debug(sorted(ack_val.items()))
                logger.debug(ack_sid)

                if callback != None : callback(ack_val)
                return ack_val

class ssl_price_worker(ssl_worker):
        def do_proc(self, arg):
                global    server_dict
                key_val, callback = arg

                price     = key_val['shot_price']
                image     = key_val['image_decode']
                sid       = key_val['sid']
                group     = key_val['group']
                host_ip   = server_dict[group]['toubiao']['ip']
                host_name = server_dict[group]['toubiao']['name']

                proto     = proto_ssl_price(key_val)
                req       = proto.make_price_req(price, image)
                head      = proto.make_ssl_head(host_name, sid)
                info_val  = self.pyget(host_ip, req, head)
                #logger.debug(sorted(info_val.items()))

                if info_val['status'] != 200 :
                        logger.error('ack status error!!!')
                        logger.error(sorted(info_val.items()))
                        #logger.error(info_val['body'].decode())
                        return

                ack_sid   = proto.get_sid_from_head(info_val['head'])
                ack_val   = proto.parse_price_ack(info_val['body'])
                #ack_val['sid'] = ack_sid
                printer.debug(sorted(ack_val.items()))
                #logger.debug(sorted(ack_val.items()))

                if callback != None : callback(ack_val)
                return ack_val

#==========================================================

class ssl_sender(pp_sender):
        def send(self, key_val, callback):
                self.put((key_val, callback))

class ssl_login_sender(ssl_sender):
        def proc(self, arg):
                worker = ssl_login_worker('ssl_login_worker')
                worker.start()
                worker.wait_for_start()
                worker.proc(arg)

class ssl_image_sender(ssl_sender):
        def proc(self, arg):
                worker = ssl_image_worker('ssl_image_worker')
                worker.start()
                worker.wait_for_start()
                worker.proc(arg)

class ssl_price_sender(ssl_sender):
        def proc(self, arg):
                worker = ssl_price_worker('ssl_price_worker')
                worker.start()
                worker.wait_for_start()
                worker.proc(arg)

#==========================================================

proc_ssl_login = ssl_login_sender()
proc_ssl_login.start()
proc_ssl_login.wait_for_start()

proc_ssl_image = ssl_image_sender()
proc_ssl_image.start()
proc_ssl_image.wait_for_start()

proc_ssl_price = ssl_price_sender()
proc_ssl_price.start()
proc_ssl_price.wait_for_start()

