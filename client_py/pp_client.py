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

TCPServer.allow_reuse_address = True
Process.daemon = True
Thread.daemon  = True

#--------------------------------------

DM_SERVER = ('', 2000)

CT_SERVER = ('', 9998)

pp_server = { 
        "login"    : ("tblogin.alltobid.com",   443),
        "toubiao"  : ("toubiao.alltobid.com",   443),
        "result"   : ("tbresult.alltobid.com",  443),
        "query"    : ("tbquery.alltobid.com",   443),
        "udp"      : ("tbudp.alltobid.com",     999),

        "login2"   : ("tblogin2.alltobid.com",  443),
        "toubiao2" : ("toubiao2.alltobid.com",  443),
        "result2"  : ("tbresult2.alltobid.com", 443),
        "query2"   : ("tbquery2.alltobid.com",  443),
        "udp2"     : ("tbudp2.alltobid.com",    999),
}

pp_bidno_dict   = {}
pp_client_dict  = {}

pp_quit         = Event()
server_dm       = None
server_ct       = None

#--------------------------------------

class ppuser():
        def __init(self):
                self.bidnumber = ''
                self.bidpass   = ''

#--------------------------------------

class bid_subthread(Thread):
        def __init__(self,bidno,bidid):
                self.bidno = bidno 
                self.bidid = bidid
                self.event_started = Event()
                self.event_warmup = Event()
                self.event_shoot = Event()
                super(bid_subthread,self).__init__()

        def started(self):
                self.event_started.wait()

        def run(self):
                print('client %s : bid thread %d : %s thread started' % (self.bidno, self.bidid, self.__class__.__name__))
                self.event_started.set()
                self.event_warmup.wait()
                self.do_warmup()
                self.event_shoot.wait()
                self.do_shoot()
                print('client %s : bid thread %d : %s thread stoped' % (self.bidno, self.bidid, self.__class__.__name__))

        def warmup(self):
                self.event_warmup.set()

        def shoot(self):
                self.event_shoot.set()

        def do_warmup(self):
                pass

        def do_shoot(self):
                pass

class bid_price(bid_subthread):
        def do_warmup(self):
                pass

        def do_shoot(self):
                pass

class bid_image(bid_subthread):
        def do_warmup(self):
                pass

        def do_shoot(self):
                pass

#--------------------------------------

class client_subthread(Thread):
        def __init__(self,bidno):
                self.bidno = bidno
                self.event_started = Event()
                super(client_subthread,self).__init__()

        def started(self):
                self.event_started.wait()
                self.event_started.clear()

class client_login(client_subthread):
        def __init__(self,bidno):
                self.event_shoot = Event()
                super(client_login,self).__init__(bidno)

        def run(self):
                print('client %s : login thread started' % (self.bidno))
                self.event_started.set()
                self.event_shoot.wait()
                self.do_shoot()
                print('client %s : login thread stoped' % (self.bidno))

        def shoot(self):
                self.event_shoot.set()

        def do_shoot(self):
                pass

class client_bid(client_subthread):
        def __init__(self,bidno,bidid):
                self.bidid = bidid
                super(client_bid,self).__init__(bidno)

        def run(self):
                print('client %s : bid thread %s started' % (self.bidno, self.bidid))
                self.image = bid_image(self.bidno,self.bidid)
                self.price = bid_price(self.bidno,self.bidid)
                self.image.start()
                self.image.started()
                self.price.start()
                self.price.started()
                self.event_started.set()
                self.image.join()
                self.price.join()
                print('client %s : bid thread %s stoped' % (self.bidno, self.bidid))

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
                return

        def run(self):
                self.event.wait()
                self.server.shutdown()
                return

class pp_subprocess(Process):
        def __init__(self,server,handler):
                self.event_stop = Event()
                self.event_started = Event()
                self.server = TCPServer(server, handler)
                self.check = check_for_stop(self.server, self.event_stop)
                super(pp_subprocess,self).__init__()
                return

        def started(self):
                self.event_started.wait()
                self.event_started.clear()
                return

        def stop(self):
                self.event_stop.set()
                return

        def run(self):
                print('Process %s started' % (self.__class__.__name__))
                self.event_started.set()
                try:
                        self.check.start()
                        self.server.serve_forever()
                except  KeyboardInterrupt:
                        pass
                print('Process %s stoped' % (self.__class__.__name__))
                return

class pp_dama(pp_subprocess):
        def __init__(self):
                super(pp_dama,self).__init__(DM_SERVER,pp_dama_handler)
                return

class pp_control(pp_subprocess):
        def __init__(self):
                super(pp_control,self).__init__(CT_SERVER,pp_control_handler)
                return

class pp_subthread(Thread):
        def __init__(self,bidno):
                self.bidno = bidno
                self.event_started = Event()
                super(pp_subthread,self).__init__()
                return

        def started(self):
                self.event_started.wait()
                self.event_started.clear()
                return

class pp_client(pp_subthread):
        def run(self):
                print('Thread %s : %s started' % (self.__class__.__name__, self.bidno))
                self.bid = []
                self.login = client_login(self.bidno)
                self.login.start()
                for i in range(3):
                        self.bid.append(client_bid(self.bidno,i))
                        self.bid[i].start()
                        self.bid[i].started()
                self.event_started.set()
                self.login.join()
                for i in range(3):
                        self.bid[i].join()
                print('Thread %s : %s stoped' % (self.__class__.__name__, self.bidno))
                return

#--------------------------------------

def pp_init_config():
        global pp_bidno_dict
        pp_bidno_dict['98765432'] = '4321'
        return

def pp_init_client():
        global pp_client_dict
        for bidno in pp_bidno_dict:
                if not bidno in pp_client_dict:
                        pp_client_dict[bidno] = pp_client(bidno)
                        pp_client_dict[bidno].start()
                        pp_client_dict[bidno].started()
        return

def pp_init_dama():
        global server_dm
        server_dm = pp_dama()
        server_dm.start()
        server_dm.started()
        return

def pp_init_control():
        global server_ct
        server_ct = pp_control()
        server_ct.start()
        server_ct.started()
        return       

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
        sleep(5)
        print('pp_quit_wait returned')
        return
        global pp_quit
        try:
                pp_quit.wait()
        except: 
                pass

def pp_main():
        pp_init_config()
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


