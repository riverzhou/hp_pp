#!/usr/bin/env python3

from redis              import StrictRedis
from readini            import pywin_config

#=============================================

def connect_redis():
        global pywin_config
        redis_passwd  = pywin_config['redis_pass']
        redis_port    = pywin_config['redis_port']
        redis_ip      = pywin_config['redis_ip']
        redis_db      = pywin_config['redis_db']
        return StrictRedis(host = redis_ip, port = redis_port, password = redis_passwd, db = redis_db)

#=============================================

if __name__ == '__main__' :
        red = connect_redis()
        print(red.dbsize())

