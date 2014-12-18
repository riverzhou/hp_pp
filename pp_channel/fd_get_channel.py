#!/usr/bin/env python3

from traceback              import print_exc, format_exc
from time                   import sleep, time

from pp_server              import pp_dns_init, pp_server_dict, pp_server_dict_2
from pp_baseredis           import pp_redis, pp_redis_init, pp_redis_connect_print
from pp_global              import pp_global_info
from pp_log                 import printer
from pp_baseclass           import pp_thread

from fd_config              import redis_dbid
from fd_channel             import fd_channel_init, channel_center
from fd_log                 import logger

#==============================================================

def getsleeptime(interval):
        return  interval - time()%interval

class fd_image(pp_thread):
        timeout_find_channel    = 1
        interval_find_channel   = 10

        def __init__(self, group):
                super().__init__()
                self.group = group 

        def main(self):
                print('get_channel %d main started' % self.group)
                while True:
                        sleep(getsleeptime(self.interval_find_channel))
                        try:
                                self.do_image()
                        except  KeyboardInterrupt:
                                pass
                        except:
                                printer.critical(format_exc())

        def do_image(self):
                global  channel_center
                channel = 'tb0'

                while True:
                        group, handle = channel_center.get_channel(channel, self.timeout_find_channel, self.group)
                        if handle == None :
                                return
                        channel_center.close_handle(handle)
                        printer.info(str(self.group) + ' : ' + str(handle) + ' closed')

get_channel  = [fd_image(0), fd_image(1)]

def get_channel_init():
        global get_channel

        get_channel[0].start()
        get_channel[1].start()

        printer.info(str(pp_server_dict))
        printer.info(str(pp_server_dict_2))

        get_channel[0].wait_for_start()
        get_channel[1].wait_for_start()

def main():
        global pp_global_info, printer

        pp_dns_init()

        if pp_redis_init()  != True:
                return

        fd_channel_init()

        get_channel_init()

        sleep(1)

        print('worker [%d] started' % redis_dbid)
        pp_global_info.event_gameover.wait()
        print('worker [%d] stopping' % redis_dbid)

        sleep(60)
        printer.wait_for_flush()
        logger.wait_for_flush()

if __name__ == '__main__':
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()
        print()

