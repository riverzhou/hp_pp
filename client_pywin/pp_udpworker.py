#!/usr/bin/env python3

#from time           import strftime, localtime, time
from traceback      import print_exc
from socket         import socket, AF_INET, SOCK_DGRAM
from socket         import timeout as sock_timeout

from pp_baseclass   import pp_thread
from pp_udpproto    import udp_proto
from pp_server      import server_dict

from pp_log         import logger, printer

#=============================================================

class udp_worker(pp_thread):
        udp_timeout = 10

        def __init__(self, console, key_val):
                global server_dict
                pp_thread.__init__(self, 'udp_worker')

                self.console     = console

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
                self.format_udp()
                while True:
                        if self.flag_stop == True: break
                        self.update_status()

        def logoff_udp(self):
             self.sock.sendto(self.proto.make_logoff_req(self.bidno, self.pid), self.server_addr)

        def client_udp(self):
             self.sock.sendto(self.proto.make_client_req(self.bidno, self.pid), self.server_addr)

        def format_udp(self):
             self.sock.sendto(self.proto.make_format_req(self.bidno, self.pid), self.server_addr)

        def update_status(self):
                udp_recv = self.recv_udp()
                if udp_recv == None:
                        return

                info_val = self.proto.parse_ack(udp_recv)
                if info_val == None:
                        return

                ctime = info_val['ltime']
                stime = info_val['systime']
                price = info_val['price']

                self.console.update_udp_info(ctime, stime, price)

        def recv_udp(self):
                while True:
                        try:
                                udp_result = self.sock.recvfrom(1500)
                        except (sock_timeout, TimeoutError):
                                return None
                        except :
                                print_exc()
                                return None

                        if self.flag_stop == True:
                                return None

                        if udp_result[1] == self.server_addr:
                                return udp_result[0]


