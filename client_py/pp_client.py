#!/usr/bin/env python3

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

TCPServer.allow_reuse_address = True
Process.daemon = True
Thread.daemon  = True

#--------------------------------------

DM_SERVER = ('', 2000)
CT_SERVER = ('', 9998)

pp_server_dict = { 
        'login'    : ('tblogin.alltobid.com',   443),
        'toubiao'  : ('toubiao.alltobid.com',   443),
        'result'   : ('tbresult.alltobid.com',  443),
        'query'    : ('tbquery.alltobid.com',   443),
        'udp'      : ('tbudp.alltobid.com',     999),
}

pp_server_dict_2 = { 
        'login'    : ('tblogin2.alltobid.com',  443),
        'toubiao'  : ('toubiao2.alltobid.com',  443),
        'result'   : ('tbresult2.alltobid.com', 443),
        'query'    : ('tbquery2.alltobid.com',  443),
        'udp'      : ('tbudp2.alltobid.com',    999),
}

pp_bidno_dict   = {}
pp_client_dict  = {}

pp_quit         = Event()
server_dm       = None
server_ct       = None

#--------------------------------------

class proto_dm():
        def __init__(self):
                pass

class proto_ct():
        def __init__(self):
                pass

class proto_udp():
        def __init__(self,client):
                self.client = client
 
        def decode(self,buff):
                pass

        def encode(self,buff):
                return self.decode(buff)


class proto_ssl():
        def __init__(self,client):
                self.client = client

        def make_req(self):
                pass

        def parse_ack(self):
                pass


class proto_udp_login(proto_udp):
        def __init__(self,client):
                super(proto_udp_login,self).__init__(client)

        def print_ack(self,buff):
                pass


class proto_ssl_login(proto_ssl):
        def __init__(self,client):
                super(proto_ssl_login,self).__init__(client)


class proto_ssl_image(proto_ssl):
        def __init__(self,client):
                super(proto_ssl_image,self).__init__(client)


class proto_ssl_price(proto_ssl):
        def __init__(self,client):
                super(proto_ssl_price,self).__init__(client)


#--------------------------------------

class bid_subthread(Thread):
        def __init__(self):
                self.event_started = Event()
                self.event_warmup = Event()
                self.event_shoot = Event()
                super(bid_subthread,self).__init__()

        def started(self):
                self.event_started.wait()

        def run(self):
                self.event_started.set()
                self.event_warmup.wait()
                self.do_warmup()
                self.event_shoot.wait()
                self.do_shoot()

        def warmup(self):
                self.event_warmup.set()

        def shoot(self):
                self.event_shoot.set()

        def do_warmup(self):
                pass

        def do_shoot(self):
                pass

class bid_price(bid_subthread):
        def __init__(self, client, bidid):
                self.client = client
                self.bidid  = bidid
                self.ssl_sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(socket(AF_INET, SOCK_STREAM))
                self.ssl_server_addr = client.server_dict["toubiao"]
                super(bid_price,self).__init__()

        def run(self):
                print('client %s : bid thread %d : %s thread started' % (self.client.bidno, self.bidid, self.__class__.__name__))
                super(bid_price,self).run()
                print('client %s : bid thread %d : %s thread stoped' % (self.client.bidno, self.bidid, self.__class__.__name__))

        def do_warmup(self):
                self.ssl_sock.connect(self.ssl_server_addr)

        def do_shoot(self):
                pass


class bid_image(bid_subthread):
        def __init__(self, client, bidid):
                self.client = client
                self.bidid  = bidid
                self.ssl_sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(socket(AF_INET, SOCK_STREAM))
                self.ssl_server_addr = client.server_dict["toubiao"]
                super(bid_image,self).__init__()

        def run(self):
                print('client %s : bid thread %d : %s thread started' % (self.client.bidno, self.bidid, self.__class__.__name__))
                super(bid_image,self).run()
                print('client %s : bid thread %d : %s thread stoped' % (self.client.bidno, self.bidid, self.__class__.__name__))

        def do_warmup(self):
                self.ssl_sock.connect(self.ssl_server_addr)

        def do_shoot(self):
                pass

#--------------------------------------

class client_subthread(Thread):
        def __init__(self):
                self.event_started = Event()
                super(client_subthread,self).__init__()

        def started(self):
                self.event_started.wait()
                self.event_started.clear()

class client_login(client_subthread):
        def __init__(self,client):
                self.client = client
                self.event_shoot = Event()
                self.ssl_sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(socket(AF_INET, SOCK_STREAM))
                self.ssl_server_addr = self.client.server_dict["login"]
                self.udp_sock = socket(AF_INET, SOCK_DGRAM)
                self.udp_sock.bind(('',0))
                self.udp_server_addr = self.client.server_dict["udp"]
                print('client %s : login bind udp_sock @%s ' % (self.client.bidno,self.udp_sock.getsockname()))
                super(client_login,self).__init__()

        def run(self):
                print('client %s : login thread started' % (self.client.bidno))
                self.event_started.set()
                self.event_shoot.wait()
                self.do_shoot()
                print('client %s : login thread stoped' % (self.client.bidno))

        def shoot(self):
                self.event_shoot.set()

        def logoff(self):
                self.udp_sock.sendto(self.client.proto_udp.logoff.make_req(),self.udp_server_addr)

        def updat_status(self):
                self.client.proto_udp_login.print_ack(self.recv_udp())          # XXX XXX XXX

        def do_shoot(self):
                self.ssl_sock.connect(self.ssl_server_addr)
                self.ssl_sock.send(self.client.proto_ssl.login.make_req())
                self.client.login_ssl_result = self.client.proto_ssl_login.parse_ack(self.ssl_sock.recv(self.client.proto_ssl_login.ack_len()))
                self.udp_sock.sendto(self.client.proto_udp_login.make_req(),self.udp_server_addr)
                self.client.login_udp_result = self.client.proto_udp.login.parse_ack(self.recv_udp())
                while True:
                        self.updat_status()
                        sleep(0)

        def recv_udp(self):
                while True:
                        udp_result = self.udp_sock.recvfrom(1500)
                        if udp_result[1] == self.udp_server_addr :
                                return udp_result[0]
                        sleep(0)

class client_bid(client_subthread):
        def __init__(self,client,bidid):
                self.client = client
                self.bidid = bidid
                super(client_bid,self).__init__()

        def run(self):
                print('client %s : bid thread %s started' % (self.client.bidno, self.bidid))
                self.image = bid_image(self.client,self.bidid)
                self.price = bid_price(self.client,self.bidid)
                self.image.start()
                self.image.started()
                self.price.start()
                self.price.started()
                self.event_started.set()
                self.image.join()
                self.price.join()
                print('client %s : bid thread %s stoped' % (self.client.bidno, self.bidid))

#--------------------------------------

class pp_control_handler(BaseRequestHandler):
        def handle(self):
                pass

class pp_dama_handler(BaseRequestHandler):
        def handle(self):
                pass

#--------------------------------------

class check_for_stop(Thread):
        def __init__(self,server,event):
                self.server = server
                self.event  = event
                super(check_for_stop,self).__init__()

        def run(self):
                self.event.wait()
                self.server.shutdown()

class pp_subprocess(Process):
        def __init__(self,server,handler):
                self.event_stop = Event()
                self.event_started = Event()
                self.server = TCPServer(server, handler)
                self.check = check_for_stop(self.server, self.event_stop)
                super(pp_subprocess,self).__init__()

        def started(self):
                self.event_started.wait()

        def stop(self):
                self.event_stop.set()

        def run(self):
                print('Process %s started' % (self.__class__.__name__))
                self.event_started.set()
                try:
                        self.check.start()
                        self.server.serve_forever()
                except  KeyboardInterrupt:
                        pass
                print('Process %s stoped' % (self.__class__.__name__))

class pp_dama(pp_subprocess):
        def __init__(self):
                super(pp_dama,self).__init__(DM_SERVER,pp_dama_handler)

class pp_control(pp_subprocess):
        def __init__(self):
                super(pp_control,self).__init__(CT_SERVER,pp_control_handler)

class pp_subthread(Thread):
        def __init__(self):
                self.event_started = Event()
                super(pp_subthread,self).__init__()

        def started(self):
                self.event_started.wait()

class pp_client(pp_subthread):
        def __init__(self,bidno_dict,server_dict):
                self.bidno = bidno_dict[0]
                self.passwd = bidno_dict[1]
                self.server_dict = server_dict
                self.proto_udp_login = proto_udp_login(self)
                self.proto_ssl_login = proto_ssl_login(self)
                self.proto_ssl_image = proto_ssl_image(self)
                self.proto_ssl_price = proto_ssl_price(self)
                super(pp_client,self).__init__()

        def run(self):
                print('Thread %s : %s started' % (self.__class__.__name__, self.bidno))
                self.bid = []
                self.login = client_login(self)
                self.login.start()
                for i in range(3):
                        self.bid.append(client_bid(self,i))
                        self.bid[i].start()
                        self.bid[i].started()
                self.event_started.set()
                for i in range(3):
                        self.bid[i].join()
                self.login.join()
                print('Thread %s : %s stoped' % (self.__class__.__name__, self.bidno))

#--------------------------------------

def pp_init_config():
        global pp_bidno_dict
        pp_bidno_dict['98765432']  = ('98765432','4321')
        pp_bidno_dict['98765431']  = ('98765431','1321')

def pp_init_dns():
        global pp_server_dict, pp_server_dict_2
        for s in pp_server_dict :
                pp_server_dict[s] = (gethostbyname(pp_server_dict[s][0]), pp_server_dict[s][1])
        for s in pp_server_dict_2 :
                pp_server_dict_2[s] = (gethostbyname(pp_server_dict_2[s][0]), pp_server_dict_2[s][1])

def pp_init_client():
        global pp_client_dict, pp_bidno_dict
        for bidno in pp_bidno_dict:
                if not bidno in pp_client_dict:
                        pp_client_dict[bidno] = pp_client(pp_bidno_dict[bidno],pp_server_dict)
                        pp_client_dict[bidno].start()
                        pp_client_dict[bidno].started()

def pp_init_dama():
        global server_dm
        server_dm = pp_dama()
        server_dm.start()
        server_dm.started()

def pp_init_control():
        global server_ct
        server_ct = pp_control()
        server_ct.start()
        server_ct.started()

def pp_stop_dama():
        global server_dm
        server_dm.stop()

def pp_stop_control():
        global server_ct
        server_ct.stop()

def pp_quit_set():
        global pp_quit
        pp_quit.set()

def pp_wait_dama():
        global server_dm
        server_dm.join()

def pp_wait_control():
        global server_ct
        server_ct.join()

def pp_quit_wait():
        global pp_quit
        sleep(5)
        print('pp_quit_wait returned')
        return
        try:
                pp_quit.wait()
        except: 
                pass

def pp_main():
        pp_init_config()
        pp_init_dns()
        pp_init_client()
        pp_init_dama()
        pp_init_control()
        pp_quit_wait()
        pp_stop_dama()
        pp_stop_control()
        pp_wait_dama()
        pp_wait_control()

#--------------------------------------

if __name__ == "__main__":
        try:
                pp_main()
        except  KeyboardInterrupt:
                pass


