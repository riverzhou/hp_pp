#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from threading                  import Thread, Event, Condition, Lock, Event, Semaphore
from struct                     import pack, unpack
from socketserver               import ThreadingTCPServer, BaseRequestHandler
from traceback                  import print_exc
from time                       import time, localtime, strftime
from hashlib                    import md5
from time                       import sleep
from socket                     import socket, gethostbyname, AF_INET, SOCK_STREAM, SOCK_DGRAM, SHUT_RDWR
import ssl
import random, string

from pp_log                     import logger, printer

from pp_thread                  import pp_subthread
from pp_proto                   import pp_server_dict, pp_server_dict_2, proto_pp_client, proto_client_login, proto_client_bid, proto_bid_image, proto_bid_price, proto_udp
from ct_proto                   import CT_SERVER, proto_ct_server

#==================================================================================================================

ThreadingTCPServer.allow_reuse_address = True
Thread.daemon  = True

event_pp_quit = Event()

pp_user_dict = {}
lock_pp_user_dict = Lock()

server_ct = None

#------------------------------------------------------------------------------------------------------------------

class bid_price(pp_subthread, proto_bid_price):
        def __init__(self, user, client, bid, bidid):
                pp_subthread.__init__(self)
                proto_bid_price.__init__(self, user, client, bid, bidid)

                self.event_warmup = bid.event_price_warmup
                self.event_shoot = bid.event_price_shoot

                self.ssl_sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(socket(AF_INET, SOCK_STREAM))
                self.ssl_server_addr = self.client.server_dict["toubiao"]['addr']

        def stop(self):
                pp_subthread.stop(self)
                self.event_warmup.set()
                self.event_shoot.set()

        def run(self):
                logger.debug('client %s : bid thread %d : %s thread started' % (self.client.bidno, self.bidid, self.__class__.__name__))
                try:
                        self.started_set()
                        while True :
                                if self.stop == True: break
                                self.event_warmup.wait()
                                if self.stop == True: break
                                self.do_warmup()
                                if self.stop == True: break
                                self.event_shoot.wait()
                                if self.stop == True: break
                                self.do_shoot()
                                break
                except  KeyboardInterrupt:
                        pass
                logger.debug('client %s : bid thread %d : %s thread stoped' % (self.client.bidno, self.bidid, self.__class__.__name__))

        def do_warmup(self):
                self.ssl_sock.connect(self.ssl_server_addr)

        def do_shoot(self):
                self.bid.lock_dict.acquire()
                price = self.bid.price_amount
                if not price in self.bid.price_sid_dict :
                        self.bid.lock_dict.release()
                        return False
                sid = self.bid.price_sid_dict[price]
                if not sid in self.bid.sid_number_dict : 
                        self.bid.lock_dict.release()
                        return False
                number = self.bid.sid_number_dict[sid]
                self.bid.lock_dict.release()
                self.ssl_sock.send(self.proto_ssl_price.make_req(price, number, sid))
                recv_ssl = self.ssl_sock.recv(self.proto_ssl_price.ack_len)
                if not recv_ssl:
                        return False
                key_val = self.proto_ssl_price.parse_ack(recv_ssl)
                return True

class bid_image(pp_subthread, proto_bid_image):
        def __init__(self, user, client, bid, bidid):
                pp_subthread.__init__(self)
                proto_bid_image.__init__(self, user, client, bid, bidid)

                #self.event_warmup = bid.event_image_warmup
                #self.event_shoot  = bid.event_image_shoot
                self.sem_warmup = bid.sem_image_warmup
                self.sem_shoot  = bid.sem_image_shoot

                #self.ssl_sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(socket(AF_INET, SOCK_STREAM))
                self.ssl_server_addr = self.client.server_dict["toubiao"]['addr']

        def stop(self):
                pp_subthread.stop(self)
                #self.event_warmup.set()
                #self.event_shoot.set()
                self.sem_warmup.release()
                self.sem_shoot.release()

        def run(self):
                logger.debug('client %s : bid thread %d : %s thread started' % (self.client.bidno, self.bidid, self.__class__.__name__))
                try:
                        self.started_set()
                        while True: 
                                if self.stop == True: break
                                #self.event_warmup.wait()
                                self.sem_warmup.acquire()
                                if self.stop == True: break
                                self.do_warmup()
                                if self.stop == True: break
                                #self.event_shoot.wait()
                                self.sem_shoot.acquire()
                                if self.stop == True: break
                                self.do_shoot()
                                self.do_cooldown()
                                sleep(0)
                except  KeyboardInterrupt:
                        pass
                logger.debug('client %s : bid thread %d : %s thread stoped' % (self.client.bidno, self.bidid, self.__class__.__name__))

        def do_warmup(self):
                self.ssl_sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(socket(AF_INET, SOCK_STREAM))
                self.ssl_sock.connect(self.ssl_server_addr)

        def do_cooldown(self):
                self.ssl_sock.shutdown(SHUT_RDWR)
                self.ssl_sock.close()

        def do_shoot(self):
                self.bid.lock_dict.acquire()
                price = self.bid.image_amount
                self.bid.lock_dict.release()
                self.ssl_sock.send(self.proto_ssl_image.make_req(price, self.client.login.sid))
                recv_ssl = self.ssl_sock.recv(self.proto_ssl_image.ack_len)
                if not recv_ssl:
                        return False
                key_val = self.proto_ssl_image.parse_ack(recv_ssl)
                sid = key_val['sid']
                image = key_val['image']
                self.send_decode_req(price, sid, image)
                return True

        def send_decode_req(self, price, sid, image):
                if self.bid.flag_pool_mode != True :
                        self.bid.lock_dict.acquire()
                        self.bid.price_amount = price
                        self.bid.price_sid_dict[price] = sid
                        self.bid.lock_dict.release()
                        self.user.handler.send_ct_image_decode(self.bidid, sid, image)
                else :
                        self.bid.lock_dict.acquire()
                        self.bid.price_sid_dict[price] = sid
                        self.bid.lock_dict.release()
                        self.user.handler.send_ct_pool_decode(self.bidid, sid, image)

#------------------------------------------------------------------------------------------------------------------

class client_bid(pp_subthread, proto_client_bid):
        def __init__(self, user, client, bidid):
                pp_subthread.__init__(self)
                proto_client_bid.__init__(self, user, client, bidid)

                self.event_price_warmup  = Event()
                self.event_price_shoot   = Event()
                #self.event_image_warmup = Event()
                #self.event_image_shoot  = Event()
                self.sem_image_warmup    = Semaphore(value=0)
                self.sem_image_shoot     = Semaphore(value=0)

                self.flag_pool_mode      = False

                self.lock_dict = Lock()
                self.price_sid_dict = {}
                self.sid_number_dict = {}

                self.image = bid_image(user, client, self, bidid)
                self.price = bid_price(user, client, self, bidid)

        def run(self):
                logger.debug('client %s : bid thread %s started' % (self.client.bidno, self.bidid))
                try:
                        self.image.start()
                        self.image.started()
                        self.price.start()
                        self.price.started()
                        self.started_set()
                        self.wait_for_stop()
                        self.image.stop()
                        self.price.stop()
                except  KeyboardInterrupt:
                        pass
                logger.debug('client %s : bid thread %s stoped' % (self.client.bidno, self.bidid))

class client_login(pp_subthread, proto_client_login):
        def __init__(self, user, client):
                pp_subthread.__init__(self)
                proto_client_login.__init__(self, user, client)

                self.event_shoot = Event()
                self.event_shoot.set()

                self.event_login_ok = Event()

                self.ssl_sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(socket(AF_INET, SOCK_STREAM))
                self.ssl_server_addr = self.client.server_dict["login"]['addr']
                self.udp_sock = socket(AF_INET, SOCK_DGRAM)
                self.udp_sock.bind(('',0))
                self.udp_server_addr = self.client.server_dict["udp"]['addr']
                logger.info('client %s : login bind udp_sock @%s ' % (self.client.bidno,self.udp_sock.getsockname()))

        def stop(self):
                pp_subthread.stop(self)
                self.event_shoot.set()
                self.event_login_ok.set()

        def run(self):
                logger.debug('client %s : login thread started' % (self.client.bidno))
                try:
                        self.started_set()
                        while True :
                                if self.stop == True: break
                                self.event_shoot.wait()
                                if self.stop == True: break
                                self.do_shoot()
                                break
                except  KeyboardInterrupt:
                        pass
                finally:
                        self.do_logoff_udp()
                logger.debug('client %s : login thread stoped' % (self.client.bidno))

        def do_shoot(self):
                self.ssl_sock.connect(self.ssl_server_addr)
                self.ssl_sock.send(self.proto_ssl_login.make_req())
                recv_ssl = self.ssl_sock.recv(self.proto_ssl_login.ack_len)
                if not recv_ssl:
                        return False
                key_val = self.proto_ssl_login.parse_ack(recv_ssl)
                self.sid = key_val['sid']
                self.pid = key_val['pid']
                self.name = key_val['name']
                self.event_login_ok.set()
                # 
                self.do_format_udp()
                self.do_client_udp()
                while True:
                        if self.stop == True:
                                break
                        self.do_update_status()
                        sleep(0)
                return True

        def wait_login_ok(self):
                self.event_login_ok.wait()
                sleep(1)

        def do_logoff_udp(self):
                self.udp_sock.sendto(self.proto_udp.make_logoff_req(), self.udp_server_addr)
                udp_recv = self.recv_udp()
                self.proto_udp.print_ack(udp_recv)
                self.proto_udp.parse_ack(udp_recv)

        def do_client_udp(self):
                self.udp_sock.sendto(self.proto_udp.make_client_req(), self.udp_server_addr)
                udp_recv = self.recv_udp()
                self.proto_udp.print_ack(udp_recv)
                self.proto_udp.parse_ack(udp_recv)

        def do_format_udp(self):
                self.udp_sock.sendto(self.proto_udp.make_format_req(), self.udp_server_addr)
                udp_recv = self.recv_udp()
                self.proto_udp.print_ack(udp_recv)
                self.proto_udp.parse_ack(udp_recv)

        def do_update_status(self):
                self.udp_sock.sendto(self.proto_udp.make_format_req(), self.udp_server_addr)
                udp_recv = self.recv_udp()
                self.proto_udp.print_info(udp_recv)
                self.proto_udp.parse_info(udp_recv)

        def recv_udp(self):
                while True:
                        udp_result = self.udp_sock.recvfrom(1500)
                        if udp_result[1] == self.udp_server_addr :
                                return udp_result[0]
                        sleep(0)

#------------------------------------------------------------------------------------------------------------------

class pp_client(pp_subthread, proto_pp_client):
        def __init__(self, user, machine, server_dict):
                pp_subthread.__init__(self)
                proto_pp_client.__init__(self, user, machine, server_dict)

                self.login = client_login(user, self)
                self.bid = []
                for i in range(3):
                        self.bid.append(client_bid(user, self, i))

        def run(self):
                logger.debug('Thread %s : %s started' % (self.__class__.__name__, self.bidno))
                try:
                        self.login.start()
                        self.login.started()
                        for i in range(3):
                                self.bid[i].start()
                                self.bid[i].started()
                        self.started_set()
                        self.wait_for_stop()
                        for i in range(3):
                                self.bid[i].stop()
                        self.login.stop()
                except  KeyboardInterrupt:
                        pass
                logger.debug('Thread %s : %s stoped' % (self.__class__.__name__, self.bidno))

#------------------------------------------------------------------------------------------------------------------

class pp_machine():
        def __init__(self, mcode = None, loginimage_number = None):
                if mcode != None :
                        self.mcode = mcode
                else:
                        self.mcode = self.create_mcode()

                if loginimage_number != None :
                        self.loginimage_number = loginimage_number
                else:
                        self.loginimage_number = self.create_number()

        def create_mcode(self):
                return ''.join([(string.ascii_letters+string.digits)[x] for x in random.sample(range(0,62),random.randint(10,20))])

        def create_number(self):
                return ''.join([(string.digits)[x] for x in random.sample(range(0,10),6)])

#------------------------------------------------------------------------------------------------------------------

class pp_user():
        def __init__(self, bidno, passwd, handler, machine):
                self.bidno = bidno
                self.passwd = passwd

                self.handler = handler

                if machine != None :
                        self.machine = machine
                else :
                        self.machine = pp_machine()

                self.client = pp_client(self, self.machine, pp_server_dict)

        def logoff(self):
                self.client.stop()

        @staticmethod
        def add_user(bidno, passwd, handler, machine = None):
                global pp_user_dict, lock_pp_user_dict
                lock_pp_user_dict.acquire()
                user = pp_user(bidno, passwd, handler, machine)
                pp_user_dict[bidno] = user
                lock_pp_user_dict.release()
                user.client.start()
                user.client.started()
                return user
        
        @staticmethod
        def del_user(bidno, passwd):
                global pp_user_dict, lock_pp_user_dict
                lock_pp_user_dict.acquire()
                pp_user_dict[bidno].logoff()
                del(pp_user_dict[bidno])
                lock_pp_user_dict.release()

#------------------------------------------------------------------------------------------------------------------

class ct_handler(proto_ct_server):

        #给 pp_client 线程的函数调用的接口
        def send_ct_image_decode(self, bidid, sessionid, image):
                self.put(self.make_proto_ct_image_decode_req(bidid, sessionid, image))
                return True

        # 给 pp_client 线程的函数调用的接口
        def send_ct_pool_decode(self, bidid, sessionid, image):
                self.put(self.make_proto_ct_pool_decode_req(bidid, sessionid, image))
                return True

        #----------------------------------------------------------------

        def proc_ct_image_decode(self, key_val):        # 把结果存入到 self..bid 的 sid_number 字典里，并发送事件
                bidid = int(key_val['BIDID'])
                sid = key_val['SESSIONID']
                number = key_val['IMAGE_NUMBER']
                #self.client.bid[bidid].sid = sid
                #self.client.bid[bidid].image_number = number
                self.client.bid[bidid].lock_dict.acquire()
                self.client.bid[bidid].sid_number_dict[sid] = number
                self.client.bid[bidid].lock_dict.release()
                self.client.bid[bidid].event_price_shoot.set()
                return True

        def proc_ct_pool_decode(self, key_val):         # 把结果存入到 self..bid 的 sid_number 字典里，不发送事件
                bidid = int(key_val['BIDID'])
                sid = key_val['SESSIONID']
                number = key_val['IMAGE_NUMBER']
                #self.client.bid[bidid].sid = sid
                #self.client.bid[bidid].image_number = number
                self.client.bid[bidid].lock_dict.acquire()
                self.client.bid[bidid].sid_number_dict[sid] = number
                self.client.bid[bidid].lock_dict.release()
                return True

        def proc_ct_image_pool(self, key_val):
                bidid = int(key_val['BIDID'])
                price = key_val['PRICE']
                self.client.bid[bidid].flag_pool_mode = True
                self.client.bid[bidid].image_amount = price
                #self.client.bid[bidid].event_image_warmup.set()
                #self.client.bid[bidid].event_image_shoot.set()
                self.client.bid[bidid].sem_image_warmup.release()
                self.client.bid[bidid].sem_image_shoot.release()
                self.put(self.make_proto_ct_image_pool_ack(bidid))
                return True

        def proc_ct_price_shoot(self, key_val):
                bidid = int(key_val['BIDID'])
                price = key_val['PRICE']
                self.client.bid[bidid].price_amount = price
                self.client.bid[bidid].event_price_shoot.set()
                self.put(self.make_proto_ct_price_shoot_ack(bidid))
                return True

        def proc_ct_image_shoot(self, key_val):
                bidid = int(key_val['BIDID'])
                price = key_val['PRICE']
                self.client.bid[bidid].image_amount = price
                #self.client.bid[bidid].event_image_shoot.set()
                self.client.bid[bidid].sem_image_shoot.release()
                self.put(self.make_proto_ct_image_shoot_ack(bidid))
                return True

        def proc_ct_image_warmup(self, key_val):
                bidid = int(key_val['BIDID'])
                #self.client.bid[bidid].event_image_warmup.set()
                self.client.bid[bidid].sem_image_warmup.release()
                self.put(self.make_proto_ct_image_warmup_ack(bidid))
                return True

        def proc_ct_price_warmup(self, key_val):
                bidid = int(key_val['BIDID'])
                self.client.bid[bidid].event_price_warmup.set()
                self.put(self.make_proto_ct_price_warmup_ack(bidid))
                return True

        def proc_ct_login(self, key_val):
                self.user = pp_user.add_user(key_val['BIDNO'], key_val['PASSWD'], self)
                self.client = self.user.client
                self.login_ok = True
                self.put(self.make_proto_ct_login_ack())
                return True

        def proc_ct_nologin(self, key_val):
                self.put(self.make_proto_ct_nologin_ack())
                return True

        def proc_ct_unknow(self, key_val):
                self.put(self.make_proto_ct_unknow_ack())
                return True

#------------------------------------------------------------------------------------------------------------------

class pp_ct(pp_subthread):
        def __init__(self):
                pp_subthread.__init__(self)
                self.server = ThreadingTCPServer(CT_SERVER, ct_handler)

        def run(self):
                logger.debug('Thread %s started' % (self.__class__.__name__))
                try:
                        self.started_set()
                        self.server.serve_forever()
                except  KeyboardInterrupt:
                        pass
                logger.debug('Thread %s stoped' % (self.__class__.__name__))

#------------------------------------------------------------------------------------------------------------------

def pp_init_user():
        machine = ct_machine()
        ct_add_user('98765432','4321', ct_handler())

def pp_init_dns():
        global pp_server_dict, pp_server_dict_2
        for s in pp_server_dict :
                pp_server_dict[s]  = {
                                        'addr' : (gethostbyname(pp_server_dict[s][0]), pp_server_dict[s][1]),
                                        'name' : pp_server_dict[s][0]}
        for s in pp_server_dict_2 :
                pp_server_dict_2[s]= {
                                        'addr' : (gethostbyname(pp_server_dict_2[s][0]), pp_server_dict_2[s][1]), 
                                        'name' : pp_server_dict_2[s][0]}

def pp_init_ct():
        global server_ct
        server_ct = pp_ct()
        server_ct.start()
        server_ct.started()

def pp_quit_set():
        global event_pp_quit
        event_pp_quit.set()

def pp_wait_quit():
        global event_pp_quit
        try:
                event_pp_quit.wait()
        except KeyboardInterrupt:
                pass

def pp_main():
        pp_init_dns()
        #pp_init_user()
        pp_init_ct()
        logger.info('Server Started ...')
        pp_wait_quit()

#--------------------------------------

if __name__ == "__main__":
        pp_main()


