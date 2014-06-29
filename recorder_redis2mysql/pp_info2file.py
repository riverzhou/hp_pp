#!/usr/bin/env python3

from mysql.connector    import connect
from redis              import StrictRedis
from traceback          import print_exc

from pp_baseclass       import pp_thread
from pp_log             import logger
from pp_config          import pp_config

#=============================================================

info_db  = 15
log_file = 'info.log'

class redis_db():
        global  pp_config, info_db
        ip      = pp_config['redis_ip']
        port    = pp_config['redis_port']
        passwd  = pp_config['redis_pass']
        db      = info_db
        key     = 'info'
        day     = pp_config['redis_day']

        def connect_redis(self):
                try:
                        return StrictRedis(host = self.ip, port = self.port, password = self.passwd, db = self.db)
                except:
                        print_exc()
                        return None

        def __init__(self):
                self.redis    = self.connect_redis()
                if self.redis == None : return None
                print('redis connect succeed')
                print()

        def get(self):
                return self.redis.lrange(self.key, 0, -1)

        def clean(self):
                return self.redis.delete(self.key)


def main():
        global  pp_config, log_file
        rdb = redis_db()
        log = open(log_file, 'a')
        buff = rdb.get()
        for line in buff:
                line = line.decode().lstrip('(').rstrip(')')
                try:
                        date, info = line.split(',', 1)
                except:
                        continue
                info = info.strip()
                info = info.strip('\'')
                date = date.strip('\'')
                day, time = date.split(' ', 1)
                time = time.split('.', 1)[0]
                if day == pp_config['redis_day'] :
                        datetime = day + ' ' + time
                        #print(datetime + '\t'+ info)
                        log.write(datetime + '\t'+ info+'\r\n')
        print()
        print('info saved into file.')

if __name__ == '__main__' :
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()
        finally:
                print()

