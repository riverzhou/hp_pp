#!/usr/bin/env python3

from time           import sleep
from random         import randint
from itertools      import repeat

from pygal          import Line, Config
from pp_db          import redis_db

from svg_mysql2dict import read_mysql2dict
from svg_createline import draw_line
from fmt_date       import *

#==============================================

intertime = 1 # 秒，支持浮点

def getsleeptime(itime):
        return itime - time()%itime

count_redis_data = 0

def read_redis_data():
        global count_redis_data
        count_redis_data += 1
        if count_redis_data > 60 :
                count_redis_data = 0
        return count_redis_data

price_increase_rate = 4
list_y = []
def create_list_y(redis_data):
        global price_increase_rate, list_y
        if redis_data == 0 : list_y = []
        y = 73000 if len(list_y) == 0 else list_y[-1]
        n = randint(0, price_increase_rate)
        if n ==  price_increase_rate:
                y += 100
        list_y.append(y)
        return list_y

def create_list_x():
        list_y = []
        for i in range(60):
                y = '11:29:%.2d' % i
                list_y.append(y)
        y = '11:29:30'
        list_y.append(y)
        return list_y

def main():
        global dict_date, list_month, intertime
        redis = redis_db()

        list_y = None
        list_x = create_list_x()
        date = '2014-06-29'
        while True :
                redis_data = read_redis_data()
                list_y = create_list_y(redis_data)
                name = 'current:price:%s:60' % date
                line = draw_line(name, list_x, list_y)
                redis.set(name, line)
                sleep(getsleeptime(intertime))

#------------------------------------------------------------------

if __name__ == '__main__':
        main()


