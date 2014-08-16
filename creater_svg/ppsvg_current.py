#!/usr/bin/env python3

from time           import time, sleep, localtime, mktime, strptime, strftime
from random         import randint
from itertools      import repeat
from pickle         import loads, dumps
from collections    import OrderedDict
from traceback      import print_exc

from pygal          import Line, Config
from pp_db          import redis_db

from svg_mysql2dict import read_mysql2dict
from svg_createline import draw_price_line
from fmt_date       import *

from pp_udpproto    import udp_proto

from pp_config      import pp_config

#==============================================

source_data = OrderedDict()

def time_sub(end, begin):
        return int(mktime(strptime('1970-01-01 '+end, '%Y-%m-%d %H:%M:%S'))) - int(mktime(strptime('1970-01-01 '+begin, '%Y-%m-%d %H:%M:%S')))

def read_redis_data(db, key, proto):
        global source_data
        info = db.blk_get_one(key).decode().split(',')[1].strip().strip('\)').strip('\'')
        data = proto.parse_ack(info)
        print(data)
        if data['code'] == 'A':
                return False
        if time_sub('11:29:00', data['systime']) > 0 or time_sub(data['systime'], '11:30:00') > 0 : 
                return False
        source_data[data['systime']] = int(data['price'])
        return True

def create_list_y(source_data):
        list_y = []
        for key in source_data :
                list_y.append(source_data[key])
        return list_y

def create_list_x():
        global source_data
        list_y = []
        for i in range(60):
                y = '11:29:%.2d' % i
                list_y.append(y)
                source_data[y] = None
        y = '11:30:00'
        list_y.append(y)
        source_data[y] = None
        return list_y

def main():
        global pp_config, source_data

        proto = udp_proto()

        source_redis = redis_db(pp_config['redis_source_db'])
        redis = redis_db()

        list_y = [None]
        list_x = create_list_x()
        date = pp_config['redis_date']

        name = 'current:price:%s:60' % date
        line = draw_price_line(name, list_x, list_y)
        redis.set(name, line)
        while True :
                if read_redis_data(source_redis, pp_config['redis_source_key'], proto) == False : continue
                list_y = create_list_y(source_data)
                name = 'current:price:%s:60' % date
                line = draw_price_line(name, list_x, list_y)
                redis.set(name, line)

#------------------------------------------------------------------

if __name__ == '__main__':
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()
        finally:
                print()


