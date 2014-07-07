#!/usr/bin/env python3

from xlrd               import open_workbook, xldate_as_tuple
from collections        import OrderedDict
from traceback          import print_exc

from pp_config          import pp_config
from fmt_date           import *
from fmt_formater       import fmt_formater
from pp_db              import mysql_db
from pp_udpproto        import udp_proto

#====================================================

date = '2014-06-29'

def covert(source):
        return (str(source[1]), source[2])

def read_log(mysql, date):
        table = 'format_origin_' + date.replace('-','_')
        list_log = mysql.read(table)
        return list(map(covert, list_log))

def write_number(mysql, date, list_data, clean = True):
        table = 'format_number_' + date.replace('-','_')
        if clean : mysql.clean_table(table)
        mysql.insert_number_list(table, list_data)

def write_price(mysql, date, list_data, clean = True):
        table = 'format_price_' + date.replace('-','_')
        if clean : mysql.clean_table(table)
        mysql.insert_price_list(table, list_data)

def parse_log(parser, date, list_log):
        list_number = []
        list_price = []
        for data in list_log:
                log = data[1].strip('\\t').strip('\\n')
                dict_info = parser.parse_info(log)
                if dict_info['code'] == 'B':
                        list_price.append((date + ' ' + dict_info['systime'], int(dict_info['price'])))
                elif dict_info['code'] == 'A':
                        list_number.append((date + ' ' + dict_info['systime'], int(dict_info['number'])))
                else:
                        continue
        return (list_price, list_number)
        
def main():
        global date
        org_mysql = mysql_db(pp_config['mysql_origin_db'])
        list_log = read_log(org_mysql, date)
        org_mysql.close()
        parser = udp_proto()
        list_price, list_number = parse_log(parser, date, list_log)
        list_format_price  = fmt_formater(list_price,  date + ' ' + '11:00:00', date + ' ' + '11:30:00')
        list_format_number = fmt_formater(list_number, date + ' ' + '10:30:00', date + ' ' + '11:00:00')
        fmt_mysql = mysql_db(pp_config['mysql_format_db'])
        write_number(fmt_mysql, date, list_format_number)
        write_price(fmt_mysql, date, list_format_price)

if __name__ == '__main__':
        main()

