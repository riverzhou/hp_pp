#!/usr/bin/env python3

from mysql.connector    import connect
from redis              import StrictRedis
from traceback          import print_exc

from pp_config          import pp_config

#=============================================================

class mysql_db():
        global  pp_config
        ip      = pp_config['mysql_ip']
        port    = pp_config['mysql_port']
        user    = pp_config['mysql_user']
        passwd  = pp_config['mysql_pass']
        db      = pp_config['mysql_db']

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

        def insert(self, table, data, commit=True):
                sql = ('INSERT INTO %s ' % table) + ('(datetime, price, count) VALUES (%s, %s, %s)')
                #print(sql)
                self.cursor.execute(sql, data)
                if commit == True : self.mysql.commit()
                print(table,'instert ok.')

        def insert_list(self, table, list_data, commit=True):
                sql = ('INSERT INTO %s ' % table) + ('(datetime, price, count) VALUES (%s, %s, %s)')
                #print(sql)
                self.cursor.executemany(sql, list_data)
                if commit == True : self.mysql.commit()
                print(table,'instert ok.')

        def read(self, table):
                sql = ('SELECT * FROM  %s ' % table)
                self.cursor.execute(sql)
                print(table,'read ok.')
                return self.cursor.fetchall()

        def clean_table(self, table):
                self.mysql.commit()
                #sql = 'DELETE FROM %s' % table
                sql = 'TRUNCATE TABLE %s' % table
                #print(sql)
                self.cursor.execute(sql)
                self.mysql.commit()
                print(table,'clean ok.')

        def close(self):
                self.cursor.close()
                self.mysql.close()

        def flush(self):
                self.mysql.commit()
                self.close()


class redis_db():
        global  pp_config
        ip      = pp_config['redis_ip']
        port    = pp_config['redis_port']
        passwd  = pp_config['redis_pass']
        db      = pp_config['redis_db']
        #key     = pp_config['redis_key']
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


#------------------------------------------------------------------------

def main():
        global  pp_config
        mdb = mysql_db()
        rdb = redis_db()

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

