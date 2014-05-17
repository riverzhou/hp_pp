#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from threading                  import Thread
from multiprocessing            import Process, Event, Condition, Lock, Event
from struct                     import pack, unpack
from socketserver               import TCPServer, BaseRequestHandler
from socket                     import socket
from traceback                  import print_exc
from time                       import time, localtime, strftime
from hashlib                    import md5
from time                       import sleep
from socket                     import socket, gethostbyname, AF_INET, SOCK_STREAM, SOCK_DGRAM 
import ssl

from pp_proto                   import pp_server_dict, pp_server_dict_2, proto_pp_client, proto_client_login, proto_client_bid, proto_bid_image, proto_bid_price
from dm_proto                   import proto_dm, dm_handler
from ct_proto                   import proto_ct, ct_handler

#==================================================================================================================

TCPServer.allow_reuse_address = True
Process.daemon = True
Thread.daemon  = True

#------------------------------------------------------------------------------------------------------------------

DM_SERVER = ('', 2000)
CT_SERVER = ('', 9998)

server_dm = None
server_ct = None

pp_bidno_dict      = {}
pp_client_dict     = {}

event_quit         = None
event_login_shoot  = None
event_image_warmup = ()
event_image_shoot  = ()
event_price_warmup = ()

#------------------------------------------------------------------------------------------------------------------

class pp_subthread(Thread):
        __metaclass__ = ABCMeta

        def __init__(self):
                Thread.__init__(self)
                self.event_started = Event()

        def started(self):
                self.event_started.wait()

        def started_set(self):
                self.event_started.set()

#------------------------------------------------------------------------------------------------------------------

class bid_price(pp_subthread, proto_bid_price):
        def __init__(self, client, bid, bidid):
                pp_subthread.__init__(self)
                proto_bid_price.__init__(self, client, bid, bidid)
                global event_price_warmup
                self.event_warmup = event_price_warmup[self.bidid]
                self.event_shoot = bid.event_price_shoot
                self.ssl_sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(socket(AF_INET, SOCK_STREAM))
                self.ssl_server_addr = self.client.server_dict["toubiao"]

        def run(self):
                print('client %s : bid thread %d : %s thread started' % (self.client.bidno, self.bidid, self.__class__.__name__))
                try:
                        self.started_set()
                        self.event_warmup.wait()
                        self.do_warmup()
                        self.event_shoot.wait()
                        self.do_shoot()
                except  KeyboardInterrupt:
                        pass
                print('client %s : bid thread %d : %s thread stoped' % (self.client.bidno, self.bidid, self.__class__.__name__))

        def do_warmup(self):
                self.ssl_sock.connect(self.ssl_server_addr)

        def do_shoot(self):
                pass

class bid_image(pp_subthread, proto_bid_image):
        def __init__(self, client, bid, bidid):
                pp_subthread.__init__(self)
                proto_bid_image.__init__(self, client, bid, bidid)
                global event_image_warmup, event_image_shoot 
                self.event_warmup = event_price_warmup[self.bidid]
                self.event_shoot = event_image_shoot[self.bidid]
                self.event_price_shoot = bid.event_price_shoot
                self.ssl_sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(socket(AF_INET, SOCK_STREAM))
                self.ssl_server_addr = self.client.server_dict["toubiao"]

        def run(self):
                print('client %s : bid thread %d : %s thread started' % (self.client.bidno, self.bidid, self.__class__.__name__))
                try:
                        self.started_set()
                        self.event_warmup.wait()
                        self.do_warmup()
                        self.event_shoot.wait()
                        self.do_shoot()
                except  KeyboardInterrupt:
                        pass
                print('client %s : bid thread %d : %s thread stoped' % (self.client.bidno, self.bidid, self.__class__.__name__))

        def do_warmup(self):
                self.ssl_sock.connect(self.ssl_server_addr)

        def do_shoot(self):
                self.bid.image_number = '654321'
                self.event_price_shoot.set()

#------------------------------------------------------------------------------------------------------------------

class client_bid(pp_subthread, proto_client_bid):
        def __init__(self, client, bidid):
                pp_subthread.__init__(self)
                proto_client_bid.__init__(self, client, bidid)
                self.event_price_shoot = Event()
                self.image = bid_image(client, self, self.bidid)
                self.price = bid_price(client, self, self.bidid)

        def run(self):
                print('client %s : bid thread %s started' % (self.client.bidno, self.bidid))
                try:
                        self.image.start()
                        self.image.started()
                        self.price.start()
                        self.price.started()
                        self.started_set()
                        self.image.join()
                        self.price.join()
                except  KeyboardInterrupt:
                        pass
                print('client %s : bid thread %s stoped' % (self.client.bidno, self.bidid))

class client_login(pp_subthread, proto_client_login):
        def __init__(self, client):
                pp_subthread.__init__(self)
                proto_client_login.__init__(self, client)
                global event_login_shoot
                self.event_shoot = event_login_shoot
                self.ssl_sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(socket(AF_INET, SOCK_STREAM))
                self.ssl_server_addr = self.client.server_dict["login"]
                self.udp_sock = socket(AF_INET, SOCK_DGRAM)
                self.udp_sock.bind(('',0))
                self.udp_server_addr = self.client.server_dict["udp"]
                print('client %s : login bind udp_sock @%s ' % (self.client.bidno,self.udp_sock.getsockname()))

        def run(self):
                print('client %s : login thread started' % (self.client.bidno))
                try:
                        self.started_set()
                        self.event_shoot.wait()
                        self.do_shoot()
                except  KeyboardInterrupt:
                        pass
                print('client %s : login thread stoped' % (self.client.bidno))

        def logoff(self):
                self.udp_sock.sendto(self.client.proto_udp_logoff.make_req(),self.udp_server_addr)      # XXX XXX XXX

        def do_update_status(self):
                self.client.proto_udp_login.print(self.recv_udp())                                      # XXX XXX XXX

        def do_shoot(self):
                self.ssl_sock.connect(self.ssl_server_addr)
                self.ssl_sock.send(self.client.proto_ssl.login.make_req())
                recv_ssl = self.ssl_sock.recv(self.client.proto_ssl_login.ack_len())
                if not recv_ssl:
                        return False
                self.client.login_ssl_result = self.client.proto_ssl_login.parse_ack(recv_ssl)
                self.udp_sock.sendto(self.client.proto_udp_login.make_req(),self.udp_server_addr)
                self.client.login_udp_result = self.client.proto_udp.login.parse_ack(self.recv_udp())
                while True:
                        self.do_update_status()
                        sleep(0)
                return True

        def recv_udp(self):
                while True:
                        udp_result = self.udp_sock.recvfrom(1500)
                        if udp_result[1] == self.udp_server_addr :
                                return udp_result[0]
                        sleep(0)

#------------------------------------------------------------------------------------------------------------------

class pp_client(pp_subthread, proto_pp_client):
        def __init__(self, bidno_dict, server_dict):
                pp_subthread.__init__(self)
                proto_pp_client.__init__(self,bidno_dict, server_dict)
                self.login = client_login(self)
                self.bid = []
                for i in range(3):
                        self.bid.append(client_bid(self,i))

        def run(self):
                print('Thread %s : %s started' % (self.__class__.__name__, self.bidno))
                try:
                        self.login.start()
                        self.login.started()
                        for i in range(3):
                                self.bid[i].start()
                                self.bid[i].started()
                        self.started_set()
                        for i in range(3):
                                self.bid[i].join()
                        self.login.join()
                except  KeyboardInterrupt:
                        pass
                print('Thread %s : %s stoped' % (self.__class__.__name__, self.bidno))

#------------------------------------------------------------------------------------------------------------------

class check_for_stop(Thread):
        def __init__(self,server,event):
                Thread.__init__(self)
                self.server = server
                self.event  = event

        def run(self):
                self.event.wait()
                self.server.shutdown()

class pp_subprocess(Process):
        __metaclass__ = ABCMeta

        def __init__(self,server_addr,handler):
                Process.__init__(self)
                self.event_stop = Event()
                self.event_started = Event()
                self.server = TCPServer(server_addr, handler)
                self.check = check_for_stop(self.server, self.event_stop)

        def started(self):
                self.event_started.wait()

        def started_set(self):
                self.event_started.set()

        def stop(self):
                self.event_stop.set()

        def run(self):
                print('Process %s started' % (self.__class__.__name__))
                try:
                        self.check.start()
                        self.started_set()
                        self.server.serve_forever()
                except  KeyboardInterrupt:
                        pass
                print('Process %s stoped' % (self.__class__.__name__))

class pp_dm(pp_subprocess):
        def __init__(self):
                pp_subprocess.__init__(self,DM_SERVER,dm_handler)

class pp_ct(pp_subprocess):
        def __init__(self):
                pp_subprocess.__init__(self,CT_SERVER,ct_handler)

#------------------------------------------------------------------------------------------------------------------

def pp_init_config():
        global pp_bidno_dict
        pp_bidno_dict['98765432']  = ('98765432','4321')
        pp_bidno_dict['98765431']  = ('98765431','1321')

def pp_init_dns():
        global pp_server_dict, pp_server_dict_2
        for s in pp_server_dict :
                pp_server_dict[s]  = (gethostbyname(pp_server_dict[s][0]), pp_server_dict[s][1], pp_server_dict[s][0])
        for s in pp_server_dict_2 :
                pp_server_dict_2[s]= (gethostbyname(pp_server_dict_2[s][0]), pp_server_dict_2[s][1], pp_server_dict_2[s][0])

def pp_init_event():
        global event_quit, event_login_shoot, event_image_warmup, event_image_shoot, event_price_warmup
        event_quit                 = Event()
        event_login_shoot          = Event()
        event_image_warmup         = (Event(),Event(),Event())
        event_image_shoot          = (Event(),Event(),Event())
        event_price_warmup         = (Event(),Event(),Event())

def pp_init_client():
        global pp_client_dict, pp_bidno_dict
        for bidno in pp_bidno_dict:
                if not bidno in pp_client_dict:
                        pp_client_dict[bidno] = pp_client(pp_bidno_dict[bidno],pp_server_dict)
                        pp_client_dict[bidno].start()
                        pp_client_dict[bidno].started()

def pp_init_dm():
        global server_dm
        server_dm = pp_dm()
        server_dm.start()
        server_dm.started()

def pp_init_ct():
        global server_ct
        server_ct = pp_ct()
        server_ct.start()
        server_ct.started()

def pp_stop_dm():
        global server_dm
        server_dm.stop()

def pp_stop_ct():
        global server_ct
        server_ct.stop()

def pp_quit_set():
        global event_quit
        event_quit.set()

def pp_wait_dm():
        global server_dm
        server_dm.join()

def pp_wait_ct():
        global server_ct
        server_ct.join()

def pp_quit_wait():
        global event_quit
        event_quit.wait()

def pp_main():
        pp_init_config()
        pp_init_dns()
        pp_init_event()
        pp_init_client()
        pp_init_dm()
        pp_init_ct()
        try:
                pp_quit_wait()
        except:
                pass
        else:                
                pp_stop_dm()
                pp_stop_ct()
        finally:                
                pp_wait_dm()
                pp_wait_ct()

#--------------------------------------

if __name__ == "__main__":
        pp_main()


