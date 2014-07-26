#!/usr/bin/env python3

from datetime       import datetime
from traceback      import print_exc
from socket         import socket, AF_INET, SOCK_DGRAM
from threading      import Lock
from time           import time, sleep, localtime, mktime, strptime, strftime

from pp_baseclass   import pp_thread
from pp_udpproto    import udp_proto
from pp_server      import server_dict

from pp_log         import logger, printer

#=============================================================

def time_sub(end, begin):
        return int(mktime(strptime('1970-01-01 '+end, '%Y-%m-%d %H:%M:%S'))) - int(mktime(strptime('1970-01-01 '+begin, '%Y-%m-%d %H:%M:%S')))

def getsleeptime(itime):
        return itime - time()%itime

#=============================================================

class price():
        def __init__(self):
                self.cur_price  = 0
                self.lock_price = Lock()

        def set(self, price):
                self.lock_price.acquire()
                try:
                        self.current_price = int(price)
                except:
                        print_exc()
                self.lock_price.release()

        def get(self):
                return self.current_price

#-------------------------------------------------------------

class udp_format(pp_thread):
        interval = 20

        def __init__(self, worker):
                pp_thread.__init__(self, 'udp_format')
                self.worker = worker

        def main(self):
                for i in range(2):
                        if self.flag_stop == True: return 
                        if self.worker.sock != None:
                                try:
                                        self.worker.format_udp()
                                except:
                                        print_exc()
                        if self.event_stop.wait(1) == True: return 

                while True:
                        if self.flag_stop == True: return 
                        if self.worker.sock != None:
                                try:
                                        self.worker.format_udp()
                                except:
                                        print_exc()
                        if self.event_stop.wait(self.interval) == True: return 


class udp_worker(pp_thread):
        udp_timeout = 10

        def __init__(self, console, key_val):
                global server_dict
                pp_thread.__init__(self, 'udp_worker')

                self.console     = console
                self.event_shot  = None
                self.price_shot  = 0

                self.list_trigger_time  = None
                self.list_trigger_event = None

                self.udp_format  = None

                self.bidno       = key_val['bidno']
                self.pid         = key_val['pid']
                self.group       = key_val['group']

                self.server_addr = server_dict[self.group]['udp']['ip'], server_dict[self.group]['udp']['port']

                self.sock        = socket(AF_INET, SOCK_DGRAM)
                self.sock.settimeout(self.udp_timeout)
                self.sock.bind(('',0))
                logger.info('Client %s : login bind udp_sock @%s ' % (self.bidno, self.sock.getsockname()))

                self.proto       = udp_proto()

        def main(self):
                self.udp_format = udp_format(self)
                self.udp_format.start()
                self.udp_format.wait_for_start()
                while True:
                        if self.flag_stop == True: break
                        self.update_status()

        def reg_trigger(self, list_time, list_event):
                self.list_trigger_time  = list_time
                self.list_trigger_event = list_event

        def reg(self, price, event):
                try:
                        int_price = int(price)
                except:
                        print_exc()
                        return
                self.price_shot = int_price
                self.event_shot = event

        def stop(self):
                if self.udp_format != None : self.udp_format.stop()
                if self.sock != None:
                        self.logoff_udp()
                        try:
                                self.sock.close()
                        except:
                                pass
                self.sock       = None
                self.event_shot = None
                self.price_shot = 0
                self.flag_stop  = True
                self.event_stop.set()

        def logoff_udp(self):
                try:
                        self.sock.sendto(self.proto.make_logoff_req(self.bidno, self.pid), self.server_addr)
                except:
                        print_exc()

        def client_udp(self):
                try:
                        self.sock.sendto(self.proto.make_client_req(self.bidno, self.pid), self.server_addr)
                except:
                        print_exc()

        def format_udp(self):
                try:
                        self.sock.sendto(self.proto.make_format_req(self.bidno, self.pid), self.server_addr)
                except:
                        print_exc()

        def update_status(self):
                udp_recv = self.recv_udp()
                if udp_recv == None:
                        return

                udp_recv = self.proto.parse_decode(udp_recv)
                info_val = self.proto.parse_ack(udp_recv)
                if info_val == None:
                        return

                code  = info_val['code']

                if code == 'F':
                        if self.console != None : self.console.update_udp_status(datetime.strftime(datetime.now(), '%H:%M:%S'))
                        return

                bidinfo = info_val['bidinfo']

                if code == 'C':
                        if self.console != None : self.console.update_bid_status(bidinfo)
                        return

                printer.critical(udp_recv)

                ctime = info_val['ltime']
                stime = info_val['systime']
                price = info_val['price']

                try:
                        int_price = int(price)
                except:
                        print_exc()
                        return

                global current_price
                current_price.set(int_price)

                self.check_shot_price(int_price)
                self.check_image_price(int_price, stime)

                if self.console != None :
                        self.console.update_udp_info(ctime, stime, price)
                        self.console.update_bid_status(bidinfo)

                printer.warning(info_val, True)

        def check_shot_price(self, cur_price):
                if self.price_shot != 0 and self.event_shot != None and self.price_shot <= cur_price + 300 and self.price_shot >= cur_price - 300:
                        try:
                                self.event_shot.set()
                        except:
                                print_exc()

        def check_image_price(self, cur_price, cur_time):
                if self.list_trigger_time == None or self.list_trigger_event == None : return
                list_t = list(map(lambda t: time_sub(cur_time, t), self.list_trigger_time))
                for n in range(len(list_t)):
                        if list_t[n] > 0 and list_t[n] <= 3 :
                                self.list_trigger_event[n] = True

        def recv_udp(self):
                while True:
                        try:
                                if self.sock != None : udp_result = self.sock.recvfrom(1500)
                        except (TimeoutError, OSError):
                                return None
                        except :
                                print_exc()
                                return None

                        if self.flag_stop == True:
                                return None

                        if udp_result[1] == self.server_addr:
                                return udp_result[0]

#==========================================================

current_price = price()



