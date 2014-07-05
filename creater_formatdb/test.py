#!/usr/bin/env python3

from collections        import OrderedDict
from traceback          import print_exc

from pp_db              import mysql_db

def clean_table(mysql):
        table = ''
        mysql.clean_table(table)

def main():
        global dict_table
        mysql = mysql_db()
        data= ('2014-01-18 11:29:00', 72600, 1)
        table = 'format_14_01_18'

        mysql.clean_table(table)

        #mysql.insert(table, data)
        #mysql.flush()

if __name__ == '__main__':
        main()

