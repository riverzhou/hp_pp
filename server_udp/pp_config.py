#!/usr/bin/env python3

from configparser       import ConfigParser

CONFIG_FILE ='pp_config.ini'

def parse_ini():
        config = ConfigParser()
        config.read(CONFIG_FILE)

        mysql_server = config['mysql_server']   if 'mysql_server' in config     else None
        udp_data = config['udp_data']           if 'udp_data' in config         else None

        key_val = {}
        if mysql_server != None :
                for key in mysql_server:
                        key_val['mysql_'+key]   = mysql_server[key]
        if udp_data != None :
                for key in udp_data:
                        key_val['udp_'+key]     = udp_data[key]

        return key_val

pp_config = parse_ini()

if __name__ == '__main__' :
        print(sorted(pp_config.items()))
