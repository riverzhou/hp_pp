#!/usr/bin/env python3

from time           import sleep
from random         import randint
from itertools      import repeat
from traceback      import print_exc

from pygal          import Line, Config
from pp_db          import redis_db

from svg_mysql2dict import read_mysql2dict
from svg_createline import draw_price_dm_line 
from fmt_date       import *
from svg_calculate  import calc_rate, calc_rate_ma

#========================================================================

def save_price_dm(redis, dict_data, time):
        global dict_date, list_price_dm_month, list_time_price_dm
        list_date = list(map(lambda x : dict_date[x], list_price_dm_month))

        list_x = []
        list_y = []
        for date in list_date:
                list_data = dict_data[date]
                for data in list_data:
                        if str(data[1]).split()[1] == time:
                                price_date = data[1]
                                price_begin = data[2]
                        elif str(data[1]).split()[1] == '11:30:00':
                                price_end = data[2]
                        else:
                                continue
                list_x.append(str(price_date).split()[0])
                list_y.append(price_end - price_begin)
        name = 'datamine:price:%s' % time
        line = draw_price_dm_line(name, list_x, list_y)
        redis.set(name, line)

#-------------------------------------------------------------------------

def main():
        global list_time_price_dm
        redis = redis_db()
        dict_data = read_mysql2dict()

        for time in list_time_price_dm:
                save_price_dm(redis, dict_data, time)

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

