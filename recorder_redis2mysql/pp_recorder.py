#!/usr/bin/env python3

from mysql.connector    import connect
from redis              import StrictRedis
from traceback          import print_exc

from pp_baseclass       import pp_thread
from pp_log             import logger
from pp_config          import pp_config

#=============================================================

class mysql_db():
        global  pp_config
        ip      = pp_config['mysql_ip']
        port    = pp_config['mysql_port']
        user    = pp_config['mysql_user']
        passwd  = pp_config['mysql_pass']
        db      = pp_config['mysql_db']
        table   = pp_config['mysql_table']

        add_udp_record = (('INSERT INTO %s ' % table) + 
               '(daytime, info) ' +
               'VALUES (%s, %s)')

        def connect_mysql(self):
                try:
                        return connect(host = self.ip, port = self.port, user = self.user, password = self.passwd, database = self.db)
                except:
                        print_exc()
                        return None

        def __init__(self):
                self.mysql    = self.connect_mysql()
                if self.mysql == None : return None
                self.cursor = self.mysql.cursor()
                print('mysql connect succeed')

        def put(self, buff):
                self.cursor.execute(self.add_udp_record, buff)

        def flush(self):
                self.mysql.commit()
                self.cursor.close()
                self.mysql.close()

class redis_db():
        global  pp_config
        ip      = pp_config['redis_ip']
        port    = pp_config['redis_port']
        passwd  = pp_config['redis_pass']
        db      = pp_config['redis_db']
        key     = pp_config['redis_key']
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

        def get(self):
                return self.redis.lrange(self.key, 0, -1)

        def clean(self):
                return self.redis.delete(self.key)

def main():
        global  pp_config
        mdb = mysql_db()
        rdb = redis_db()

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
                        datetime = date + ' ' + time
                        #print(datetime, info)
                        mdb.put((datetime, info))
        mdb.flush()
        print('date saved into mysql.')

if __name__ == '__main__' :
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()
        finally:
                print()

