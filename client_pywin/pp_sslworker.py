#!/usr/bin/env python3

#==========================================================

from pp_log             import logger, printer
from threading          import Thread, Event, Lock, Semaphore
from queue              import Queue, LifoQueue, Empty
from traceback          import print_exc

from http.client        import HTTPSConnection, HTTPConnection
from socket             import timeout as sock_timeout
from time               import sleep

from pp_baseclass       import pp_thread, pp_sender
from pp_server          import server_dict
from readini            import pywin_config
from pp_udpworker       import current_price
from pp_sslproto        import *

#==========================================================

class ssl_worker(pp_thread):
        connect_timeout = 60

        def __init__(self, key_val, manager, info = '', delay = 0):
                pp_thread.__init__(self, info)
                self.lock_close = Lock()
                self.flag_closed= False
                self.info       = info
                self.delay      = delay
                self.manager    = manager
                self.event_proc = Event()
                self.arg        = None
                self.handler    = None
                self.host_ip    = key_val['host_ip']
                self.host_name  = key_val['host_name']
                self.group      = key_val['group']
                self.timeout    = key_val['timeout'] if 'timeout' in key_val else None

        def close(self):
                if self.handler != None:
                        try:
                                self.handler.close()
                        except:
                                print_exc()
                        finally:
                                self.handler = None

        def main(self):
                if self.delay != 0 : sleep(self.delay)
                while True:
                        self.handler = HTTPSConnection(self.host_ip, timeout = self.timeout)
                        self.handler._http_vsn = 10
                        self.handler._http_vsn_str = 'HTTP/1.0'
                        try:
                                self.handler.connect()
                        except (sock_timeout, TimeoutError):
                                self.close()
                                continue
                        except:
                                print_exc()
                                continue
                        break
                self.manager.feedback('connected', self.group, self)
                ev = self.event_proc.wait(self.connect_timeout)
                self.lock_close.acquire()
                self.flag_closed = True
                self.lock_close.release()
                if self.flag_stop == True:
                        self.close()
                        return
                if ev != True :
                        self.manager.feedback('timeout', self.group, self)
                if self.arg == None:
                        self.close()
                        return
                self.do_proc(self.arg)

        def put(self, arg):
                self.lock_close.acquire()
                if self.flag_closed != True:
                        self.arg = arg
                        self.lock_close.release()
                else:
                        self.lock_close.release()
                        return False
                self.event_proc.set()
                return True

        def do_proc(self, arg): pass

        def pyget(self, req, headers = {}):
                try:
                        self.handler.request('GET', req, headers = headers)
                except:
                        self.close()
                        self.manager.feedback('err_write', self.group, self)
                        print_exc()
                        return None
                try:
                        ack  = self.handler.getresponse()
                        body = ack.read()
                except:
                        self.close()
                        self.manager.feedback('err_read', self.group, self)
                        print_exc()
                        return None
                #--------------------------------------------------------
                self.close()
                self.manager.feedback('done', self.group, self)

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

                if info_val == None:
                        return

                if info_val['status'] != 200 :
                        logger.error('ack status error : %s' % info_val['status'])
                        printer.error('ack status error : %s' % info_val['status'])
                        try:
                                logger.error(info_val['body'].decode('gb18030'))
                                printer.error(info_val['body'].decode('gb18030'))
                        except: pass
                        else:
                                return
                        try:
                                logger.error(info_val['body'].decode())
                                printer.error(info_val['body'].decode())
                        except: pass
                        else:
                                return
                        logger.error('unknow body coding')
                        printer.error(info_val['body'])
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

                if info_val == None:
                        return

                if info_val['status'] != 200 :
                        logger.error('ack status error : %s' % info_val['status'])
                        printer.error('ack status error : %s' % info_val['status'])
                        try:
                                logger.error(info_val['body'].decode('gb18030'))
                                printer.error(info_val['body'].decode('gb18030'))
                        except: pass
                        else:
                                return
                        try:
                                logger.error(info_val['body'].decode())
                                printer.error(info_val['body'].decode())
                        except: pass
                        else:
                                return
                        logger.error('unknow body coding')
                        printer.error(info_val['body'])
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
                event     = key_val['event']
                delay     = key_val['delay']
                worker_in = key_val['worker_in']
                worker_out= key_val['worker_out']
                group     = self.group

                worker_in(group)

                proto     = proto_ssl_price(key_val)
                req       = proto.make_price_req(price, image)
                head      = proto.make_ssl_head(self.host_name, sid)

                int_price = int(price)
                event.wait()
                if delay != 0 : sleep(delay)
                global current_price
                cur_price = current_price.get()
                logger.debug('shot_price %d , cur_price %d ' % (int_price, cur_price))
                if int_price > cur_price + 300 or int_price < cur_price - 300:
                        worker_out(group)
                        return

                info_val  = self.pyget(req, head)
                #logger.debug(sorted(info_val.items()))

                if info_val == None:
                        worker_out(group)
                        return

                if info_val['status'] != 200 :
                        logger.error('ack status error : %s' % info_val['status'])
                        printer.error('ack status error : %s' % info_val['status'])
                        try:
                                logger.error(info_val['body'].decode('gb18030'))
                                printer.error(info_val['body'].decode('gb18030'))
                        except: pass
                        else:
                                worker_out(group)
                                return
                        try:
                                logger.error(info_val['body'].decode())
                                printer.error(info_val['body'].decode())
                        except: pass
                        else:
                                worker_out(group)
                                return
                        logger.error('unknow body coding')
                        printer.error(info_val['body'])
                        worker_out(group)
                        return

                ack_sid   = proto.get_sid_from_head(info_val['head'])
                ack_val   = proto.parse_price_ack(info_val['body'])
                #ack_val['sid'] = ack_sid
                printer.debug(sorted(ack_val.items()))
                #logger.debug(sorted(ack_val.items()))

                worker_out(group)
                if callback != None : callback(ack_val)

#==========================================================

class ssl_sender(pp_sender):
        console = None

        def send(self, key_val, callback):
                self.put((key_val, callback))

        def feedback(self, status, group, worker):
                logger.debug(worker.info + ' : ' + str(group) + ' : ' + status)

        def set_pool_size(self, size):
                self.pool_size = size

        def reg(self, console):
                self.console = console

class ssl_login_sender(ssl_sender):
        def proc(self, arg):
                global server_dict
                group   = arg[0]['group']
                key_val = {}
                key_val['host_ip']      = server_dict[group]['login']['ip']
                key_val['host_name']    = server_dict[group]['login']['name']
                key_val['group']        = group
                key_val['timeout']      = None
                worker = ssl_login_worker(key_val, self, 'ssl_login_worker')
                worker.start()
                worker.wait_for_start()
                worker.put(arg)

#----------------------------------------------------------

class ssl_image_pool_maker(pp_thread):
        max_worker = 100

        def __init__(self, manager, info = '', delay = 0):
                pp_thread.__init__(self, info)
                self.manager = manager
                self.delay   = delay

        def main(self):
                count = 0
                while True:
                        pool_size       = self.manager.pool_size
                        dsize           = [0,0]
                        qsize           = [0,0]
                        qsize[0]        = self.manager.queue_workers[0].qsize()
                        qsize[1]        = self.manager.queue_workers[1].qsize()
                        delay           = int(pool_size/10)
                        if delay  < 1   : delay = 1
                        if self.manager.flag_start_pool == True:
                                dsize[0] = pool_size - qsize[0]
                                dsize[1] = pool_size - qsize[1]
                                for i in range(dsize[0]):
                                        if self.manager.worker_on_way[0] > 3 * dsize[0] or qsize[0] + self.manager.worker_on_way[0] > self.max_worker:
                                                break
                                        try:
                                                worker  = ssl_image_worker(self.manager.key_val[0], self.manager, None, int(i/delay))
                                                worker.start()
                                        except:
                                                print_exc()
                                        else:
                                                self.manager.lock_worker_on_way[0].acquire()
                                                self.manager.worker_on_way[0] += 1
                                                self.manager.lock_worker_on_way[0].release()
                                for i in range(dsize[1]):
                                        if self.manager.worker_on_way[1] > 3 * dsize[1] or qsize[1] + self.manager.worker_on_way[1] > self.max_worker:
                                                break
                                        try:
                                                worker  = ssl_image_worker(self.manager.key_val[1], self.manager, None, int(i/delay))
                                                worker.start()
                                        except:
                                                print_exc()
                                        else:
                                                self.manager.lock_worker_on_way[1].acquire()
                                                self.manager.worker_on_way[1] += 1
                                                self.manager.lock_worker_on_way[1].release()
                        if self.manager.console != None:
                                goal    = pool_size
                                if qsize[0] < 100 and qsize[1] < 100:
                                        current = '%.2d : %.2d' % (qsize[0], qsize[1])
                                else:
                                        current = '%.3d : %.3d' % (qsize[0], qsize[1])
                                if self.manager.worker_on_way[0] < 100 and self.manager.worker_on_way[1] < 100:
                                        onway   = '%.2d : %.2d' % (self.manager.worker_on_way[0], self.manager.worker_on_way[1])
                                else:
                                        onway   = '%.3d : %.3d' % (self.manager.worker_on_way[0], self.manager.worker_on_way[1])
                                self.manager.console.update_image_channel(current, goal, onway)
                        sleep(1)

class ssl_image_sender(ssl_sender):
        timeout   = None

        def __init__(self, info = '', lifo = False):
                ssl_sender.__init__(self, info, lifo)
                global pywin_config
                self.pool_size = int(pywin_config['thread_image_size'])
                self.queue_workers      = (Queue(), Queue())
                self.lock_worker_on_way = (Lock(), Lock())
                self.worker_on_way      = [0,0]
                self.flag_start_pool    = False
                self.last_worker        = None
                self.key_val = ({},{})
                self.key_val[0]['host_ip']      = server_dict[0]['toubiao']['ip']
                self.key_val[0]['host_name']    = server_dict[0]['toubiao']['name']
                self.key_val[0]['group']        = 0
                self.key_val[0]['timeout']      = self.timeout
                self.key_val[1]['host_ip']      = server_dict[1]['toubiao']['ip']
                self.key_val[1]['host_name']    = server_dict[1]['toubiao']['name']
                self.key_val[1]['group']        = 1
                self.key_val[1]['timeout']      = self.timeout
                self.maker  = ssl_image_pool_maker(self, 'ssl_image_pool_maker')
                self.maker.start()
                self.maker.wait_for_start()

        def set_pool_start(self):
                self.flag_start_pool = True

        def feedback(self, status, group, worker):
                if status == 'timeout' :
                        self.queue_workers[group].get()
                        return

                if status == 'connected' :
                        self.queue_workers[group].put(worker)
                        self.lock_worker_on_way[group].acquire()
                        self.worker_on_way[group] -= 1
                        self.lock_worker_on_way[group].release()
                        return

        def proc(self, arg):
                global server_dict
                group   = arg[0]['group']
                key_val = {}
                key_val['host_ip']      = server_dict[group]['toubiao']['ip']
                key_val['host_name']    = server_dict[group]['toubiao']['name']
                key_val['timeout']      = None
                while True:
                        try:
                                worker = self.queue_workers[group].get_nowait()
                        except Empty:
                                logger.error('ssl_image_sender Queue %d is empty' % group)
                                return
                        except:
                                print_exc()
                                return
                        else:
                                if self.last_worker != None :
                                        self.last_worker.stop()
                                        self.last_worker.close()
                                        self.last_worker = worker
                                if worker.put(arg) == True :
                                        return

#----------------------------------------------------------

class ssl_price_pool_maker(pp_thread):
        max_worker = 100

        def __init__(self, manager, info = '', delay = 0):
                pp_thread.__init__(self, info)
                self.manager = manager
                self.delay   = delay

        def main(self):
                count = 0
                while True:
                        pool_size       = self.manager.pool_size
                        dsize           = [0,0]
                        qsize           = [0,0]
                        qsize[0]        = self.manager.queue_workers[0].qsize()
                        qsize[1]        = self.manager.queue_workers[1].qsize()
                        delay           = int(pool_size/10)
                        if delay  < 1   : delay = 1
                        if self.manager.flag_start_pool == True:
                                dsize[0] = pool_size - qsize[0]
                                dsize[1] = pool_size - qsize[1]
                                for i in range(dsize[0]):
                                        if self.manager.worker_on_way[0] > 3 * dsize[0] or qsize[0] + self.manager.worker_on_way[0] > self.max_worker:
                                                break
                                        try:
                                                worker  = ssl_price_worker(self.manager.key_val[0], self.manager, None, int(i/delay))
                                                worker.start()
                                        except:
                                                print_exc()
                                        else:
                                                self.manager.lock_worker_on_way[0].acquire()
                                                self.manager.worker_on_way[0] += 1
                                                self.manager.lock_worker_on_way[0].release()
                                for i in range(dsize[1]):
                                        if self.manager.worker_on_way[1] > 3 * dsize[1] or qsize[1] + self.manager.worker_on_way[1] > self.max_worker:
                                                break
                                        try:
                                                worker  = ssl_price_worker(self.manager.key_val[1], self.manager, None, int(i/delay))
                                                worker.start()
                                        except:
                                                print_exc()
                                        else:
                                                self.manager.lock_worker_on_way[1].acquire()
                                                self.manager.worker_on_way[1] += 1
                                                self.manager.lock_worker_on_way[1].release()
                        if self.manager.console != None:
                                goal    = pool_size
                                if qsize[0] < 100 and qsize[1] < 100:
                                        current = '%.2d : %.2d' % (qsize[0], qsize[1])
                                else:
                                        current = '%.3d : %.3d' % (qsize[0], qsize[1])
                                if self.manager.worker_on_way[0] < 100 and self.manager.worker_on_way[1] < 100:
                                        onway   = '%.2d : %.2d' % (self.manager.worker_on_way[0], self.manager.worker_on_way[1])
                                else:
                                        onway   = '%.3d : %.3d' % (self.manager.worker_on_way[0], self.manager.worker_on_way[1])
                                self.manager.console.update_price_channel(current, goal, onway)
                        sleep(1)

class ssl_price_sender(ssl_sender):
        timeout   = None

        def __init__(self, info = '', lifo = False):
                ssl_sender.__init__(self, info, lifo)
                global pywin_config
                self.pool_size = int(pywin_config['thread_price_size'])
                self.queue_workers      = (Queue(), Queue())
                self.lock_worker_on_way = (Lock(), Lock())
                self.worker_on_way      = [0,0]
                self.flag_start_pool    = False
                self.key_val = ({},{})
                self.key_val[0]['host_ip']      = server_dict[0]['toubiao']['ip']
                self.key_val[0]['host_name']    = server_dict[0]['toubiao']['name']
                self.key_val[0]['group']        = 0
                self.key_val[0]['timeout']      = self.timeout
                self.key_val[1]['host_ip']      = server_dict[1]['toubiao']['ip']
                self.key_val[1]['host_name']    = server_dict[1]['toubiao']['name']
                self.key_val[1]['group']        = 1
                self.key_val[1]['timeout']      = self.timeout
                self.maker  = ssl_price_pool_maker(self, 'ssl_price_pool_maker')
                self.maker.start()
                self.maker.wait_for_start()

        def set_pool_start(self):
                self.flag_start_pool = True

        def feedback(self, status, group, worker):
                if status == 'timeout' :
                        self.queue_workers[group].get()
                        return

                if status == 'connected' :
                        self.queue_workers[group].put(worker)
                        self.lock_worker_on_way[group].acquire()
                        self.worker_on_way[group] -= 1
                        self.lock_worker_on_way[group].release()
                        return

        def proc(self, arg):
                global server_dict
                flag    = [True,True]
                worker  = [None,None]
                key_val = ({},{})
                key_val[0]['host_ip']      = server_dict[0]['toubiao']['ip']
                key_val[0]['host_name']    = server_dict[0]['toubiao']['name']
                key_val[0]['timeout']      = None
                key_val[1]['host_ip']      = server_dict[1]['toubiao']['ip']
                key_val[1]['host_name']    = server_dict[1]['toubiao']['name']
                key_val[1]['timeout']      = None
                while True:
                        if flag[0] == True:
                                try:
                                        worker[0] = self.queue_workers[0].get_nowait()
                                except Empty:
                                        flag[0]   = False
                                        logger.error('ssl_price_sender Queue 0 is empty')
                                except:
                                        flag[0]   = False
                                        print_exc()
                                else:
                                        if worker[0].put(arg) == True :
                                                flag[0] = False
                        if flag[1] == True:
                                try:
                                        worker[1] = self.queue_workers[1].get_nowait()
                                except Empty:
                                        flag[1]   = False
                                        logger.error('ssl_price_sender Queue 1 is empty')
                                except:
                                        flag[1]   = False
                                        print_exc()
                                else:
                                        if worker[1].put(arg) == True :
                                                flag[1]   = False
                        if flag[0] != True and flag[1] != True:
                                return

#==========================================================

proc_ssl_login = ssl_login_sender('proc_ssl_login')
proc_ssl_login.start()
proc_ssl_login.wait_for_start()

proc_ssl_image = ssl_image_sender('proc_ssl_image')
proc_ssl_image.start()
proc_ssl_image.wait_for_start()

proc_ssl_price = ssl_price_sender('proc_ssl_price')
proc_ssl_price.start()
proc_ssl_price.wait_for_start()

