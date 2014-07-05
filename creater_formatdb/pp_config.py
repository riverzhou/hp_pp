#!/usr/bin/env python3

from configparser       import ConfigParser

CONFIG_FILE ='pp_config.ini'

def parse_ini():
        config = ConfigParser()
        config.read(CONFIG_FILE)

        mysql_server = config['mysql_server']   if 'mysql_server' in config     else None
        redis_server = config['redis_server']   if 'redis_server' in config     else None
        excel_file   = config['excel_file']     if 'excel_file'   in config     else None

        key_val = {}
        if mysql_server != None :
                for key in mysql_server:
                        key_val['mysql_'+key]   = mysql_server[key]
        if redis_server != None :
                for key in redis_server:
                        key_val['redis_'+key]   = redis_server[key]

        if excel_file   != None :
                for key in excel_file:
                        key_val['excel_'+key]   = excel_file[key]

        return key_val

pp_config = parse_ini()

if __name__ == '__main__' :
        print(sorted(pp_config.items()))
