#!/usr/bin/env python3

from traceback              import print_exc, format_exc
from datetime               import datetime
from socket                 import socket, AF_INET, SOCK_DGRAM, timeout
from threading              import Lock
from queue                  import Queue, LifoQueue
from time                   import time, sleep, localtime, mktime, strptime, strftime

from pp_baseclass           import pp_thread
from pp_udpproto            import udp_proto
from pp_server              import server_dict
from pp_log                 import logger, printer

#=================================================

class udp_format(pp_thread):
        interval = 20

        def __init__(self, worker):
                super().__init__(worker.bidno)
                self.worker = worker

        def main(self):
                for i in range(2):
                        if self.flag_stop == True: return
                        if self.worker.sock != None:
                                try:
                                        self.worker.format_udp()
                                except:
                                        printer.critical(format_exc())
                        if self.event_stop.wait(1) == True: return

                while True:
                        if self.flag_stop == True: return
                        if self.worker.sock != None:
                                try:
                                        self.worker.format_udp()
                                except:
                                        printer.critical(format_exc())
                        if self.event_stop.wait(self.interval) == True: return


class udp_worker(pp_thread):
        udp_timeout = 10

        def __init__(self, acount, group):
                global server_dict
                super().__init__(acount[0])

                self.current_code   = None
                self.last_code      = None

                self.bidno          = acount[0]
                self.pid            = acount[1]
                self.group          = group

                self.server_addr    = server_dict[group]['udp']['ip'], server_dict[group]['udp']['port']

                self.sock           = socket(AF_INET, SOCK_DGRAM)
                self.sock.settimeout(self.udp_timeout)
                self.sock.bind(('',0))

                self.proto          = udp_proto()
                self.udp_format     = udp_format(self)


        def stop(self):
                if self.udp_format != None : self.udp_format.stop()
                if self.sock != None:
                        self.logoff_udp()
                        try:
                                self.sock.close()
                        except:
                                pass
                supper().stop()

        def logoff_udp(self):
                try:
                        self.sock.sendto(self.proto.make_logoff_req(self.bidno, self.pid), self.server_addr)
                except:
                        printer.critical(format_exc())

        def client_udp(self):
                try:
                        self.sock.sendto(self.proto.make_client_req(self.bidno, self.pid), self.server_addr)
                except:
                        printer.critical(format_exc())

        def format_udp(self):
                try:
                        self.sock.sendto(self.proto.make_format_req(self.bidno, self.pid), self.server_addr)
                except:
                        printer.critical(format_exc())

        def recv_udp(self):
                while True:
                        try:
                                if self.sock != None:
                                        udp_result = self.sock.recvfrom(1500)
                        except  (timeout, OSError):
                                return None
                        except:
                                printer.critical(format_exc())
                                return None
                        if self.flag_stop == True:
                                return None
                        if udp_result[1] == self.server_addr:
                                return udp_result[0]

        def update_status(self):
                global global_info
                udp_recv = self.recv_udp()
                if udp_recv == None:
                        return

                udp_recv = self.proto.parse_decode(udp_recv)
                info_val = self.proto.parse_ack(udp_recv)
                if info_val == None:
                        return

                code  = info_val['code']

                if code == 'F':
                        printer.debug(udp_recv)
                        return

                if code == 'C':
                        printer.info(udp_recv)
                        return

                if code == 'A' or code == 'B':
                        printer.warning(udp_recv)
                        printer.debug(udp_recv)
                        return

                printer.error(udp_recv)
                return


        def main(self):
                self.udp_format.start()
                self.udp_format.wait_for_start()
                while True:
                        if self.flag_stop == True: break
                        try:
                                self.update_status()
                        except  KeyboardInterrupt:
                                break
                        except:
                                printer.critical(format_exc())
                                sleep(0)

class udp_manager(pp_thread):
        max_count_worker = 4

        def __init__(self):
                super().__init__()
                self.count_worker   = 0
                self.lock_worker    = Lock()
                self.queue_worker   = Queue()
                self.list_worker    = []

        def main(self):
                group = 0
                while True:
                        account = self.queue_worker.get()
                        group = 1 if group == 0 else 0
                        worker = udp_worker(account, group)
                        self.list_worker.append(worker)
                        worker.start()

        def add(self, account):
                self.lock_worker.acquire()
                count_worker = self.count_worker
                self.count_worker += 1
                self.lock_worker.release()
                if count_worker >= self.max_count_worker:
                        return
                self.queue_worker.put(account)

#------------------------------------------------------

daemon_udp = udp_manager()

def fd_udp_init():
        daemon_udp.start()
        daemon_udp.wait_for_start()


if __name__ == '__main__':
        fd_udp_init()
        daemon_udp.wait_for_stop()
