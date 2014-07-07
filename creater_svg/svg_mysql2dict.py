#!/usr/bin/env python3

from xlrd               import open_workbook, xldate_as_tuple
from collections        import OrderedDict
from traceback          import print_exc
from time               import time, localtime, mktime, strptime, strftime

from pp_config          import pp_config
from pp_db              import mysql_db
from fmt_date           import *

#=================================================

def time_sub(end, begin):
        return int(mktime(strptime('1970-01-01 '+end, '%Y-%m-%d %H:%M:%S'))) - int(mktime(strptime('1970-01-01 '+begin, '%Y-%m-%d %H:%M:%S')))

def read_mysql2dict(begin = '11:29:00', end = '11:30:00', mode = 'price'):
        global dict_date, list_month, pp_config
        mysql = mysql_db()
        dict_data = OrderedDict()
        if mode == 'price':
                prefix = 'format_price_'
        elif mode == 'number':
                prefix = 'format_number_'
        else:
                return dict_data
        for m in list_month:
                table = prefix + dict_date[m].replace('-','_')
                list_data = mysql.read(table)
                if list_data == None : continue
                list_out = []
                for data in list_data:
                        time = str(data[1]).split()[1]
                        if time_sub(time, begin) >= 0 and time_sub(end, time) >= 0:
                                list_out.append(data)
                dict_data[dict_date[m]] = list_out
        mysql.close()
        return dict_data

#====================================================

def main():
        dict_data = read_mysql2dict('11:29:00', '11:30:00')
        print(dict_data)

if __name__ == '__main__':
        main()

