#!/usr/bin/env python3

from mysql.connector    import connect
from redis              import StrictRedis
from traceback          import print_exc

from pp_config          import pp_config
from pp_db              import redis_db

#=============================================================

info_db  = 15
log_file = 'info.log'

def main():
        global  pp_config, log_file, info_db
        rdb = redis_db(info_db)
        log = open(log_file, 'a')
        buff = rdb.get(pp_config['redis_key'])
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
        log.close()
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

