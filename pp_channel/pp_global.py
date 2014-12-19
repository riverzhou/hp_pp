#!/usr/bin/env python3

from time           import sleep
from threading      import Event, Lock


timeout_channel     = 110
interval_channel    = 1

#========================================================================

def time_sub(end, begin):
        try:
                e = end.split(':')
                b = begin.split(':')
                return (int(e[0])*3600 + int(e[1])*60 + int(e[2])) - (int(b[0])*3600 + int(b[1])*60 + int(b[2]))
        except:
                return -1

class pp_global():
        def __init__(self):
                global timeout_channel, interval_channel
                self.event_config_init  = Event()
                self.flag_create_toubiao= [False, False]
                self.flag_gameover      = False
                self.event_gameover     = Event()
                self.timeout_channel    = [timeout_channel, interval_channel]

        def set_game_over(self):
                self.flag_gameover = True
                self.event_gameover.set()

        def update_systime(self, stime):
                self.lock_systime.acquire()
                if time_sub(stime, self.sys_time) > 0:
                        self.sys_time = stime
                self.lock_systime.release()

#--------------------------------------------

pp_global_info = pp_global()

