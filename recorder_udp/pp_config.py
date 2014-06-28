#!/usr/bin/env python3

from configparser       import ConfigParser

CONFIG_FILE ='pp_config.ini'

def parse_ini():
        config = ConfigParser()
        config.read(CONFIG_FILE)

        udp_account  = config['udp_account']    if 'udp_account'  in config     else None
        redis_server = config['redis_server']   if 'redis_server' in config     else None

        key_val = {}
        if udp_account != None :
                for key in udp_account:
                        key_val['udp_'+key]     = udp_account[key]
        if redis_server != None :
                for key in redis_server:
                        key_val['redis_'+key]   = redis_server[key]

        return key_val

pp_config = parse_ini()

if __name__ == '__main__' :
        print(sorted(pp_config.items()))
