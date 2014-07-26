#!/usr/bin/env python3

from configparser       import ConfigParser

CONFIG_FILE ='pp_config.ini'

def parse_ini():
        config = ConfigParser()
        config.read(CONFIG_FILE)

        thread_pool  = config['thread_pool']    if 'thread_pool'  in config     else None
        redis_server = config['redis_server']   if 'redis_server' in config     else None
        trigger_time = config['trigger_time']   if 'trigger_time' in config     else None

        key_val = {}
        if thread_pool != None :
                for key in thread_pool:
                        key_val['thread_'+key]  = thread_pool[key]
        if redis_server != None :
                for key in redis_server:
                        key_val['redis_'+key]   = redis_server[key]
        if trigger_time != None :
                for key in trigger_time:
                        key_val['trigger_'+key] = trigger_time[key]

        return key_val

pp_config = parse_ini()

if __name__ == '__main__' :
        print(sorted(pp_config.items()))
