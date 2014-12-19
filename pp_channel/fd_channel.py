#!/usr/bin/env python3

from threading              import Event, Lock
from queue                  import Queue, Empty
from time                   import sleep, time
from datetime               import datetime
from http.client            import HTTPSConnection, HTTPConnection
from traceback              import print_exc, format_exc

from pp_log                 import printer
from pp_server              import server_dict

from pp_global              import pp_global_info
from pp_baseclass           import pp_thread

#=============================================================================

def time_sub(end, begin):
        try:
                e = datetime.timestamp(datetime.strptime(end,   '%Y-%m-%d %H:%M:%S.%f'))
                b = datetime.timestamp(datetime.strptime(begin, '%Y-%m-%d %H:%M:%S.%f'))
                return e-b
        except:
                return -1

def getsleeptime(interval):
        if interval == 0:
                return interval
        return  interval - time()%interval

class fd_channel():
        timeout_find_channel = 0.3

        def __init__(self):
                self.queue = [{},{}]
                self.queue[0]['tb0']        = Queue()
                self.queue[1]['tb0']        = Queue()

                self.count_login_request    = 0
                self.lock_login_request     = Lock()
                self.lock_get_channel       = Lock()

        def check_channel(self, channel_handle_tuple):
                global pp_global_info
                cur_time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                time     = channel_handle_tuple[0]
                handle   = channel_handle_tuple[1]
                if time_sub(cur_time, time) < pp_global_info.timeout_channel[0]:
                        return True
                else:
                        self.close_handle(handle)
                        return False

        def find_channel(self, channel, group):
                if group == -1:
                        channel_group = 1 if self.queue[0][channel].qsize() <= self.queue[1][channel].qsize() else 0
                else:
                        channel_group = group
                channel_handle_tuple = None
                try:
                        channel_handle_tuple = self.queue[channel_group][channel].get(True, self.timeout_find_channel)
                except  KeyboardInterrupt:
                        return channel_group, None
                except  Empty:
                        return channel_group, None
                except:
                        printer.critical(format_exc())
                        return channel_group, None
                return  channel_group, channel_handle_tuple

        def get_channel(self, channel, timeout, group = -1):
                channel_group  = None
                channel_handle = None
                start = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                while True:
                        if timeout != None and time_sub(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f'), start) > timeout:
                                break
                        channel_group, channel_handle_tuple = self.find_channel(channel, group)
                        if channel_handle_tuple == None :
                                sleep(0)
                                continue
                        if self.check_channel(channel_handle_tuple) != True :
                                sleep(0)
                                continue
                        channel_handle = channel_handle_tuple[1]
                        if channel_handle == None:
                                sleep(0)
                                continue
                        break

                printer.debug(
                        'fd_channel : tb0[0] %d tb0[1] %d'
                        % (self.queue[0]['tb0'].qsize(), self.queue[1]['tb0'].qsize())
                        )

                return  channel_group, channel_handle

        def put_channel(self, channel, group, handle):
                printer.warning('put_channel : ' + str(group) + ' ' + str(handle))
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                channel_handle_tuple = (time, handle)
                return  self.queue[group][channel].put(channel_handle_tuple)

        def close_handle(self, handle):
                try:
                        handle.close()
                        del(handle)
                except:
                        printer.critical(format_exc())

        def pyget(self, handle, req, headers = {}):
                time_req = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')

                printer.info(time_req + ' :: ' + str(headers) + ' :: ' + req)

                ack = None

                try:
                        handle.request('GET', req, headers = headers)
                except  KeyboardInterrupt:
                        self.close_handle(handle)
                        return False
                except:
                        printer.critical(format_exc())
                        self.close_handle(handle)
                        return False
                try:
                        ack  = handle.getresponse()
                except  KeyboardInterrupt:
                        self.close_handle(handle)
                        return False
                except:
                        printer.critical(format_exc())
                        self.close_handle(handle)
                        return False

                self.close_handle(handle)

                try:
                        body = ack.read()
                except  KeyboardInterrupt:
                        del(ack)
                        return None
                except:
                        printer.critical(format_exc())
                        del(ack)
                        return None

                key_val = {}
                key_val['head']    = str(ack.msg)
                key_val['status']  = ack.status
                try:
                        key_val['body'] = body.decode('gb18030')
                except:
                        printer.error(body)
                        key_val['body'] = ''

                time_ack = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')

                printer.info(time_ack + ' :: ' + str(key_val['head']) + ' :: ' + str(key_val['body']))

                printer.time(time_req + ' --- ' + time_ack + ' :: ' + str(headers) + ' :: ' + req + ' :: ' + str(key_val['head']) + ' :: ' + str(key_val['body']))

                del(ack)
                return key_val

#===================================

class pp_channel_maker(pp_thread):
        def __init__(self, manager, server, group, channel):
                super().__init__(None)
                self.manager = manager
                self.server  = server
                self.group   = group
                self.channel = channel

        def main(self):
                self.create_channel()

        def create_channel(self):
                global channel_center, server_dict
                self.manager.maker_in()
                host   = server_dict[self.group][self.server]['ip']
                handle = HTTPSConnection(host)
                handle._http_vsn = 10
                handle._http_vsn_str = 'HTTP/1.0'
                try:
                        handle.connect()
                except  KeyboardInterrupt:
                        pass
                except:
                        printer.critical(format_exc())
                else:
                        channel_center.put_channel(self.channel, self.group, handle)
                self.manager.maker_out()

class pp_toubiao_channel_manager(pp_thread):
        max_onway       = 100

        def __init__(self, id):
                super().__init__()
                self.lock_onway   = Lock()
                self.number_onway = 0
                self.id = id

        def main(self):
                global pp_global_info
                while True:
                        try:
                                time_interval = float(pp_global_info.timeout_channel[1])
                        except:
                                time_interval = 2
                        sleep(getsleeptime(time_interval))
                        self.manage_channel()

        def manage_channel(self):
                global pp_global_info
                if pp_global_info.flag_gameover == True:
                        return
                if self.number_onway >= self.max_onway:
                        return
                channel = 'tb0'
                try:
                        maker = [pp_channel_maker(self, 'toubiao', 0, channel), pp_channel_maker(self, 'toubiao', 1, channel)]
                except:
                        printer.critical(format_exc())
                        return
                maker[0].start()
                maker[1].start()

        def maker_in(self):
                self.lock_onway.acquire()
                self.number_onway += 1
                self.lock_onway.release()
                
        def maker_out(self):
                self.lock_onway.acquire()
                self.number_onway -= 1
                self.lock_onway.release()

#================================================

channel_center = fd_channel()

toubiao = pp_toubiao_channel_manager(0)

def fd_channel_init():
        global toubiao
        toubiao.start()
        toubiao.wait_for_start()

#================================================

def main():
        pp_dns_init()
        pp_redis_init()
        fd_channel_init()
        pp_global_info.event_gameover.wait()

if __name__ == '__main__':
        from pp_server      import pp_dns_init
        from pp_baseredis   import pp_redis_init
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()
        print()

