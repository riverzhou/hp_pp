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
from svg_createline import draw_price_line, draw_number_line
#from fmt_date       import *

from pp_udpproto    import udp_proto

from pp_config      import pp_config

#==============================================

source_data_a = OrderedDict()
source_data_b = OrderedDict()

def time_sub(end, begin):
        return int(mktime(strptime('1970-01-01 '+end, '%Y-%m-%d %H:%M:%S'))) - int(mktime(strptime('1970-01-01 '+begin, '%Y-%m-%d %H:%M:%S')))

def time_add(time, second):
        ret = strftime('%Y-%m-%d %H:%M:%S', localtime(int(mktime(strptime('1970-01-01 '+time, "%Y-%m-%d %H:%M:%S"))) + second))
        return ret.split()[1]

def read_redis_data(db, key, proto):
        global source_data_a, source_data_b
        info = db.blk_get_one(key).decode().split(',')[1].strip().strip('\)').strip('\'')
        data = proto.parse_ack(info)
        print(data)
        if data['code'] == 'A':
                source_data_a[data['systime']] = int(data['number'])
                return 'A'
        if data['code'] == 'B' and time_sub(data['systime'], '11:29:00') >= 0 and time_sub(data['systime'], '11:30:00') <= 0:
                source_data_b[data['systime']] = int(data['price'])
                return 'B'
        return  False

def create_list_y(source_data):
        list_y = []
        for key in source_data :
                list_y.append(source_data[key])
        return list_y

def create_list_ax():
        global source_data
        list_y = []
        for i in range(1800):
                y = time_add('10:30:00', i)
                list_y.append(y)
                source_data_a[y] = None
        y = '11:00:00'
        list_y.append(y)
        source_data_a[y] = None
        return list_y

def create_list_bx():
        global source_data
        list_y = []
        for i in range(60):
                y = time_add('11:29:00', i)
                list_y.append(y)
                source_data_b[y] = None
        y = '11:30:00'
        list_y.append(y)
        source_data_b[y] = None
        return list_y

def main():
        global pp_config, source_data

        proto = udp_proto()

        source_redis = redis_db(pp_config['redis_source_db'])
        redis = redis_db()

        list_ay = [None]
        list_ax = create_list_ax()
        list_by = [None]
        list_bx = create_list_bx()

        #date = pp_config['redis_date']

        name_number = 'current:number'
        line_number = draw_number_line(name_number, list_ax, list_ay)
        redis.set(name_number, line_number)

        name_price  = 'current:price'
        line_price  = draw_price_line(name_price, list_bx, list_by)
        redis.set(name_price, line_price)

        while True :
                code = read_redis_data(source_redis, pp_config['redis_source_key'], proto)
                if code == 'B':
                        list_by     = create_list_y(source_data_b)
                        line_price  = draw_price_line(name_price, list_bx, list_by)
                        redis.set(name_price, line_price)
                        continue
                if code == 'A':
                        list_ay     = create_list_y(source_data_a)
                        line_number = draw_number_line(name_number, list_ax, list_ay)
                        redis.set(name_number, line_number)
                        continue

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


