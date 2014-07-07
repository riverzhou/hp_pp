#!/usr/bin/env python3

from collections        import OrderedDict
from pickle             import dumps, loads
from traceback          import print_exc

from pp_config          import pp_config
from pp_db              import mysql_db, redis_db
from fmt_date           import *

from svg_mysql2dict     import read_mysql2dict

#=================================================

def fmt_mysql2redis(data_mysql):
        date = str(data_mysql[1])
        price = data_mysql[2]
        coute = data_mysql[3]
        return (date, price, coute)

def fmt_dict2redis(dict_mysql):
        dict_redis = OrderedDict()
        for date in dict_mysql:
                list_redis = list(map(fmt_mysql2redis,dict_mysql[date]))
                dict_redis[date] = list_redis
        return dict_redis

def write_dict2redis(dict_redis, t = 'price'):
        redis = redis_db()
        if t == 'price':
                prefix = 'format_price_'
        elif t == 'number':
                prefix = 'format_number_'
        else:
                return 
        for date in dict_redis:
                list_redis = dict_redis[date]
                key = prefix + date.replace('-','_')
                redis.set(key, list_redis)
                print('%s save to redis ok' % key)

#====================================================

def price_m2r():
        dict_data = read_mysql2dict()
        dict_redis = fmt_dict2redis(dict_data)
        write_dict2redis(dict_redis)

def number_m2r():
        dict_data = read_mysql2dict('number')
        dict_redis = fmt_dict2redis(dict_data)
        write_dict2redis(dict_redis, 'number')

def main():
        price_m2r()
        number_m2r()

if __name__ == '__main__':
        main()

