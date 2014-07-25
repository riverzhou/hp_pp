#!/usr/bin/env python3

from time           import sleep
from random         import randint
from itertools      import repeat
from traceback      import print_exc

from pygal          import Line, Config
from pp_db          import redis_db

from svg_mysql2dict import read_mysql2dict
from svg_createline import create_price_line, create_multi_price_line, create_number_line
from fmt_date       import *
from svg_calculate  import calc_rate, calc_rate_ma

#========================================================================

def save_price_line(redis, dict_data):
        global dict_date, list_price_month
        list_date = list(map(lambda x : dict_date[x], list_price_month))
        for date in list_date:
                list_data = dict_data[date]
                name = 'history:price:%s:60' % date
                line = create_price_line(name, list_data)
                redis.set(name, line)


def save_multi_price_line(redis, dict_data):
        name = 'history:price:multi-2014:60'
        line = create_multi_price_line(name, dict_data)
        redis.set(name, line)


def save_number_line(redis, dict_data):
        global dict_date, list_number_month
        list_date = list(map(lambda x : dict_date[x], list_number_month))
        for date in list_date:
                list_data = dict_data[date]
                name = 'history:number:%s:full' % date
                line = create_number_line(name, list_data)
                redis.set(name, line)

def save_rate_line(redis, dict_data):
        global dict_date, list_number_month
        list_date = list(map(lambda x : dict_date[x], list_number_month))
        for date in list_date:
                list_data = dict_data[date]
                list_rate = calc_rate(list_data)
                name = 'history:rate:%s:full' % date
                line = create_number_line(name, list_rate)
                redis.set(name, line)

def save_rate_ma_line(redis, dict_data, ma=5):
        global dict_date, list_number_month
        list_date = list(map(lambda x : dict_date[x], list_number_month))
        for date in list_date:
                list_data = dict_data[date]
                list_rate = calc_rate_ma(list_data, ma)
                #list_rate = calc_rate(list_data)
                name = 'history:rate_ma:%s:full' % date
                line = create_number_line(name, list_rate)
                redis.set(name, line)

#-------------------------------------------------------------------------

def main():
        redis = redis_db()

        dict_data = read_mysql2dict()
        save_price_line(redis, dict_data)
        save_multi_price_line(redis, dict_data)

        dict_data = read_mysql2dict('10:30:00', '11:00:00', 'number')
        save_number_line(redis, dict_data)

        #dict_data = read_mysql2dict('10:30:00', '11:00:00', 'number')
        save_rate_line(redis, dict_data)

        #dict_data = read_mysql2dict('10:30:00', '11:00:00', 'number')
        save_rate_ma_line(redis, dict_data, 10)

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

