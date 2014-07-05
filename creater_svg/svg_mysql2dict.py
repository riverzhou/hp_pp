#!/usr/bin/env python3

from xlrd               import open_workbook, xldate_as_tuple
from collections        import OrderedDict
from traceback          import print_exc

from pp_config          import pp_config
from pp_db              import mysql_db
from fmt_date           import *

#=================================================

def read_mysql2dict():
        global dict_table, dict_date, list_month, pp_config
        mysql = mysql_db()
        dict_data = OrderedDict()
        for m in list_month:
                table = dict_table[m]
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

