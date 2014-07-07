#!/usr/bin/env python3

from xlrd               import open_workbook, xldate_as_tuple
from collections        import OrderedDict
from traceback          import print_exc

from pp_config          import pp_config
from fmt_date           import *
from fmt_formater       import fmt_formater
from pp_db              import mysql_db

#====================================================

def read_excel(file_name, col_time, col_price):
        global dict_date, list_month
        origin_data = {}
        data = open_workbook(file_name)
        for m in list_month:
                origin_data[m] = []
                table = data.sheet_by_name(m)
                i = 1
                while True:
                        try:
                                row = table.row_values(i)
                        except  IndexError:
                                break
                        except:
                                print_exc()
                                break
                        if row == None : break
                        if row[col_price] == '' : break
                        price = row[col_price]
                        price = int(price)
                        time = xldate_as_tuple(row[col_time],0)
                        time = [time[3],time[4],time[5]]
                        time = map(lambda x:'%.2d'%x, time)
                        time = ':'.join(time)
                        datetime = dict_date[m] + ' ' + time
                        origin_data[m].append((datetime,price))
                        i += 1
        return origin_data

def fmt_readexcel2list():
        global dict_date, list_month, pp_config
        name = pp_config['excel_name']
        colt = int(pp_config['excel_colt'])
        colp = int(pp_config['excel_colp'])
        origin_data = read_excel(name, colt, colp)
        format_data = OrderedDict()
        for m in list_month:
                date = dict_date[m]
                time = dict_price_time[m]
                time_begin = date + ' ' + time[0]
                time_end   = date + ' ' + time[1]
                format_data[m] = fmt_formater(origin_data[m], time_begin, time_end)
        return format_data

def main():
        global dict_table, pp_config
        mysql = mysql_db(pp_config['mysql_format_db'])
        format_data = fmt_readexcel2list()
        for m in format_data:
                list_data = format_data[m]
                table = 'format_price_' + dict_date[m].replace('-','_')
                mysql.clean_table(table)
                mysql.insert_price_list(table, list_data)
        mysql.flush()

if __name__ == '__main__':
        main()

