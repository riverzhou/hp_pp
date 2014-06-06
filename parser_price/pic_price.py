#!/usr/bin/env python3

import numpy 
from   matplotlib           import pyplot, font_manager
from   matplotlib.ticker    import MultipleLocator, FuncFormatter
from   sys                  import argv

plfonts = font_manager.FontProperties(fname='./msyh.ttf')
MultipleLocator.MAXTICKS = 3600

def formatter_x(x, p):
        global list_x
        x = int(x)
        if x >= len(list_x) or x < 0 : 
                return ''
        return list_x[x]

def set_locator(mode, list_x, list_y):
        pyplot.ylim(int(min(list_y)-100), int(max(list_y))+300)
        xaxis = pyplot.gca().xaxis
        yaxis = pyplot.gca().yaxis

        xaxis.set_major_locator(MultipleLocator(1))
        xaxis.set_minor_locator(MultipleLocator(1))
        xaxis.set_major_formatter(FuncFormatter( formatter_x))
        yaxis.set_major_locator(MultipleLocator(100))
        yaxis.set_minor_locator(MultipleLocator(100))
        for label in xaxis.get_ticklabels():
                label.set_rotation(45)
        for line  in xaxis.get_ticklines(minor=True):
                line.set_markersize(10)
        for line  in yaxis.get_ticklines(minor=True):
                line.set_markersize(10)

def create_pic(key_val):
        global list_x
        mode            = key_val['mode']
        list_x          = key_val['list_x']
        list_y          = key_val['list_y']
        label_x         = key_val['label_x']
        label_y         = key_val['label_y']
        name_line       = key_val['name_line']
        name_title      = key_val['name_title']
        name_file       = key_val['name_file']  if 'name_file' in key_val else None

        pyplot.figure(figsize = (16,9))
        pyplot.plot(list(range(len(list_x))), list_y, label = name_line,  color='red')
        pyplot.xlabel(label_x,   fontproperties = plfonts)
        pyplot.ylabel(label_y,   fontproperties = plfonts)
        pyplot.title(name_title, fontproperties = plfonts)
        pyplot.subplots_adjust(bottom = 0.15)
        set_locator(mode, list_x, list_y)
        pyplot.grid()
        pyplot.legend()
        if name_file != None : pyplot.savefig(name_file)
        pyplot.show()

def read_file(name_file):
        f = open(name_file, 'r')
        x = []
        y = []
        for line in f.readlines():
                x.append(line.split("-")[0].strip())
                y.append(line.split("-")[1].strip())
        f.close()
        return x, y

def check_argv(argv):
        if len(argv) != 2                         : return usage()
        if argv [1] != '60' and argv [1] != '30'  : return usage()
        return True

def usage():
        print   (
                './pic_price.py  60\n'+
                './pic_price.py  30\n'
                )
        return False

def main(mode):
        x, y = read_file('b_%s.res' % mode)
        key_val = {}
        key_val['mode']         = mode
        key_val['list_x']       = x
        key_val['list_y']       = [int(item) for item in y]
        key_val['label_x']      = '时间(秒)'
        key_val['label_y']      = '价格(元)'
        key_val['name_title']   = '拍 牌 投 标 - 下 半 场'
        key_val['name_line']    = 'Price'
        key_val['name_file']    = ('b_%s.png' % mode)
        create_pic(key_val)       

if __name__ == '__main__':
        if check_argv(argv) : main(argv[1])

