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
        def __init__(self, key_val, manager, info = ''):
                pp_thread.__init__(self, info)
                self.info       = info
                self.manager    = manager
                self.event_proc = Event()
                self.arg        = None
                self.handler    = None
                self.host_ip    = key_val['host_ip']
                self.host_name  = key_val['host_name']
                self.timeout    = key_val['timeout'] if 'timeout' in key_val else None

        def close(self):
                if self.handler != None :
                        try:
                                self.handler.close()
                        except:
                                print_exc()

        def main(self):
                while True:
                        self.handler = HTTPSConnection(self.host_ip, timeout = self.timeout)
                        self.handler._http_vsn = 10
                        self.handler._http_vsn_str = 'HTTP/1.0'
                        try:
                                self.handler.connect()
                        except (sock_timeout, TimeoutError):
                                self.handler.close()
                                continue
                        except:
                                print_exc()
                                continue
                        break
                self.manager.feedback('connected', self)
                self.event_proc.wait()
                self.do_proc(self.arg)

        def put(self, arg):
                self.arg = arg
                self.event_proc.set()

        def do_proc(self, arg): pass

        def pyget(self, req, headers = {}):
                try:
                        self.handler.request('GET', req, headers = headers)
                except:
                        self.close()
                        self.manager.feedback('err_write', self)
                        print_exc()
                        return None
                try:
                        ack  = self.handler.getresponse()
                        body = ack.read()
                except:
                        self.close()
                        self.manager.feedback('err_read', self)
                        print_exc()
                        return None
                #--------------------------------------------------------
                self.close()
                self.manager.feedback('done', self)

                key_val = {}
                key_val['body']    = body
                key_val['head']    = str(ack.msg)
                key_val['status']  = ack.status

                return key_val

class ssl_login_worker(ssl_worker):
        def do_proc(self, arg):
                key_val, callback = arg

                proto     = proto_ssl_login(key_val)
                req       = proto.make_login_req()
                head      = proto.make_ssl_head(self.host_name)
                info_val  = self.pyget(req, head)
                #logger.debug(sorted(info_val.items()))

                if info_val == None :
                        return

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

class ssl_image_worker(ssl_worker):
        def do_proc(self, arg):
                key_val, callback = arg

                price     = key_val['image_price']

                proto     = proto_ssl_image(key_val)
                req       = proto.make_image_req(price)
                head      = proto.make_ssl_head(self.host_name)
                info_val  = self.pyget(req, head)
                #logger.debug(sorted(info_val.items()))

                if info_val == None :
                        return

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

class ssl_price_worker(ssl_worker):
        def do_proc(self, arg):
                key_val, callback = arg

                price     = key_val['shot_price']
                image     = key_val['image_decode']
                sid       = key_val['sid']

                proto     = proto_ssl_price(key_val)
                req       = proto.make_price_req(price, image)
                head      = proto.make_ssl_head(self.host_name, sid)
                info_val  = self.pyget(req, head)
                #logger.debug(sorted(info_val.items()))

                if info_val == None :
                        return

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

#==========================================================

class ssl_sender(pp_sender):
        def send(self, key_val, callback):
                self.put((key_val, callback))

        def feedback(self, status, worker):
                logger.debug(worker.info + ' : ' + status)

class ssl_login_sender(ssl_sender):
        def proc(self, arg):
                global server_dict
                group   = arg[0]['group']
                key_val = {}
                key_val['host_ip']      = server_dict[group]['login']['ip']
                key_val['host_name']    = server_dict[group]['login']['name']
                key_val['timeout']      = None
                worker = ssl_login_worker(key_val, self, 'ssl_login_worker')
                worker.start()
                worker.wait_for_start()
                worker.put(arg)

class ssl_image_sender(ssl_sender):
        def proc(self, arg):
                global server_dict
                group   = arg[0]['group']
                key_val = {}
                key_val['host_ip']      = server_dict[group]['toubiao']['ip']
                key_val['host_name']    = server_dict[group]['toubiao']['name']
                key_val['timeout']      = None
                worker = ssl_image_worker(key_val, self, 'ssl_image_worker')
                worker.start()
                worker.wait_for_start()
                worker.put(arg)

class ssl_price_sender(ssl_sender):
        def proc(self, arg):
                global server_dict
                group   = arg[0]['group']
                key_val = {}
                key_val['host_ip']      = server_dict[group]['toubiao']['ip']
                key_val['host_name']    = server_dict[group]['toubiao']['name']
                key_val['timeout']      = None
                worker = ssl_price_worker(key_val, self, 'ssl_price_worker')
                worker.start()
                worker.wait_for_start()
                worker.put(arg)

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

