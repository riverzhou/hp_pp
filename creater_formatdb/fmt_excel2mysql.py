#!/usr/bin/env python3

from xlrd               import open_workbook, xldate_as_tuple
from collections        import OrderedDict
from traceback          import print_exc

from pp_config          import pp_config
from fmt_formater       import fmt_formater
from pp_db              import mysql_db

#=================================================

list_month = ['1月','2月','3月','4月','5月','6月']

dict_date = {
        '1月' : '2014-01-18' ,
        '2月' : '2014-02-15' ,
        '3月' : '2014-03-15' ,
        '4月' : '2014-04-19' ,
        '5月' : '2014-05-24' ,
        '6月' : '2014-06-29' ,
        }

dict_time = {
        '1月' : ('11:29:00', '11:30:00' ),
        '2月' : ('11:29:00', '11:30:00' ),
        '3月' : ('11:29:00', '11:30:00' ),
        '4月' : ('11:29:00', '11:30:00' ),
        '5月' : ('11:29:00', '11:30:00' ),
        '6月' : ('11:28:00', '11:30:00' ),
        }

dict_table = {
        '1月' : 'format_14_01_18' ,
        '2月' : 'format_14_02_15' ,
        '3月' : 'format_14_03_15' ,
        '4月' : 'format_14_04_19' ,
        '5月' : 'format_14_05_24' ,
        '6月' : 'format_14_06_29' ,
        }

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
                time = dict_time[m]
                time_begin = date + ' ' + time[0]
                time_end   = date + ' ' + time[1]
                dict_format = fmt_formater(origin_data[m], time_begin, time_end)
                format_data[m] = []
                for time in dict_format:
                        format_data[m].append(dict_format[time])
        return format_data

def main():
        global dict_table
        mysql = mysql_db()
        format_data = fmt_readexcel2list()
        for m in format_data:
                list_data = format_data[m]
                table = dict_table[m]
                mysql.clean_table(table)
                mysql.insert_list(table, list_data)
        mysql.flush()

if __name__ == '__main__':
        main()

