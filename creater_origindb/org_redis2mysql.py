#!/usr/bin/env python3

from mysql.connector    import connect
from redis              import StrictRedis
from traceback          import print_exc

from pp_config          import pp_config
from pp_db              import mysql_db, redis_db

#=============================================================

def main():
        global  pp_config
        mdb = mysql_db(pp_config['mysql_origin_db'])
        rdb = redis_db(pp_config['redis_db'])

        redis_key = pp_config['redis_key']
        redis_day = pp_config['redis_day']

        buff = rdb.get(redis_key)
        list_data = []
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
                day = redis_day # XXX XXX XXX
                if day == redis_day :
                        datetime = day + ' ' + time
                        list_data.append((datetime, info))
        prefix = 'format_origin_'
        table = prefix + redis_day.replace('-','_')
        mdb.clean_table(table)
        mdb.insert_log_list(table, list_data)
        mdb.flush()
        print('date saved into mysql.')

#=============================================================

if __name__ == '__main__' :
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()
        finally:
                print()

