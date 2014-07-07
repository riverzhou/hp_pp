#!/usr/bin/env python3

from xlrd               import open_workbook, xldate_as_tuple
from collections        import OrderedDict
from traceback          import print_exc

from pp_config          import pp_config
from pp_db              import mysql_db
from fmt_date           import *

#=================================================

def read_mysql2dict(t = 'price'):
        global dict_date, list_month, pp_config
        mysql = mysql_db()
        dict_data = OrderedDict()
        if t == 'price':
                prefix = 'format_price_'
        elif t == 'number':
                prefix = 'format_number_'
        else:
                return dict_data
        for m in list_month:
                table = prefix + dict_date[m].replace('-','_')
                list_data = mysql.read(table)
                if list_data == None : continue
                dict_data[dict_date[m]] = list_data
        mysql.close()
        return dict_data

#====================================================

def main():
        dict_data = read_mysql2dict()
        print(dict_data)

if __name__ == '__main__':
        main()

