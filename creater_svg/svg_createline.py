#!/usr/bin/env python3

from time           import sleep
from random         import randint
from itertools      import repeat
from collections    import OrderedDict

from pygal          import Line, Config
from pp_db          import redis_db

#==============================================

def draw_line(name, list_x, list_y):
        line = Line()
        line.disable_xml_declaration = True
        line.js = []

        line.x_label_rotation = 45
        line.y_labels_major_every = 3
        line.show_legend = False
        line.print_values = False
        line.width  = 1280
        line.height = 720
        line.value_formatter = lambda x:str(int(x))
        #line.major_label_font_size = 20
        #line.print_zeroes = True
        #line.show_minor_x_labels = True
        #line.show_minor_y_labels = True

        line.title = name 
        line.range = (min(list_y)-100, max(list_y)+300)
        line.x_labels = list_x
        line.add(name, list_y)
        return line.render()

def draw_multi_line(name, dict_data):
        line = Line()
        line.disable_xml_declaration = True
        line.js = []

        line.x_label_rotation = 45
        line.y_labels_major_every = 3
        #line.show_legend = False
        line.legend_at_bottom = True
        line.print_values = False
        line.width  = 1280
        line.height = 720
        line.value_formatter = lambda x:str(int(x))
        #line.major_label_font_size = 20
        #line.print_zeroes = True
        #line.show_minor_x_labels = True
        #line.show_minor_y_labels = True

        line.title = name
        min_y = None
        max_y = None
        for name in dict_data:
                #print(name)
                list_x, list_y = dict_data[name]
                line.x_labels = map(str, list_x)
                line.add(name, list_y)
                min_list_y = min(list_y)
                max_list_y = max(list_y)
                if min_y == None or min_list_y < min_y : min_y = min_list_y
                if max_y == None or max_list_y > max_y : max_y = max_list_y
        if min_y == None : min_y = 0
        if max_y == None : max_y = 0 
        line.range = (min_y-100, max_y+300)
        return line.render()
 
def create_line(name, list_data):
        list_x = []
        list_y = []
        for d in list_data:
                list_x.append(str(d[1]).split()[1])
                list_y.append(d[2])
        return draw_line(name, list_x, list_y)

def create_multi_line(name, dict_data):
        dict_data_new = OrderedDict()
        for date in dict_data:
                list_data = dict_data[date]
                list_x = []
                list_y = []
                for d in list_data:
                        list_x.append(str(d[1]).split()[1])
                        list_y.append(d[2])
                dict_data_new[date] = ((list_x,list_y))
        return draw_multi_line(name, dict_data_new)

#------------------------------------------------------------------

def main():
        global dict_date, list_month
        redis = redis_db()
        dict_data = read_mysql2dict()
        list_date = list(map(lambda x : dict_date[x], list_month))
        date = '2014-05-24'
        list_data = dict_data[date]
        name = 'history:price:%s:60' % date
        line = create_line(name, list_data)
        name = name.replace('-','_')
        print(name)
        print(line)

if __name__ == '__main__':
        from svg_mysql2dict import read_mysql2dict
        from fmt_date       import *
        main()


