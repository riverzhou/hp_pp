#!/usr/bin/env python3

from collections        import OrderedDict
from time               import time, localtime, mktime, strptime, strftime

#============================================================================

def time_sub(end, begin):
        return int(mktime(strptime(end, '%Y-%m-%d %H:%M:%S'))) - int(mktime(strptime(begin, '%Y-%m-%d %H:%M:%S')))

def time_add(time, second):
        return strftime('%Y-%m-%d %H:%M:%S', localtime(int(mktime(strptime(time, "%Y-%m-%d %H:%M:%S"))) + second))

def fmt_formater(list_origin, begin, end):
        dict_format = OrderedDict()
        list_format = []
        n = time_sub(end, begin) + 1
        for i in range(n):
                time = time_add(begin, i)
                dict_format[time] = [time, 0, 0]
        for data in list_origin:
                time, price = data
                if time in dict_format:
                        if price > dict_format[time][1] : dict_format[time][1] = price
                        dict_format[time][2] += 1
        pre_price = 0
        for time in dict_format:
                if dict_format[time][1] == 0 : dict_format[time][1] = pre_price
                if dict_format[time][1] > pre_price : pre_price = dict_format[time][1]
        for time in dict_format:
                list_format.append(tuple(dict_format[time]))
        return list_format

