#!/usr/bin/env python3

import numpy 
from   matplotlib           import pyplot, font_manager
from   matplotlib.ticker    import MultipleLocator, FuncFormatter

plfonts = font_manager.FontProperties(fname='./msyh.ttf')
#Locator.MAXTICKS = 3600
MultipleLocator.MAXTICKS = 100000

def formatter_x(x, p):
        global list_x
        x = int(x)
        if x >= len(list_x) or x < 0 : 
                return ''
        return list_x[x]

def set_locator(mode, list_x, list_y):
        pyplot.ylim(0, max(list_y))
        xaxis = pyplot.gca().xaxis
        yaxis = pyplot.gca().yaxis
        if mode == '60' :
                xaxis.set_major_locator(MultipleLocator(1))
                xaxis.set_minor_locator(MultipleLocator(1))
                xaxis.set_major_formatter(FuncFormatter( formatter_x))
                yaxis.set_major_locator(MultipleLocator(max(int(int((int(max(list_y))-int(min(list_y)))/(len(list_x)/2))/100)*100, 100)))
                yaxis.set_minor_locator(MultipleLocator(100))
                for label in xaxis.get_ticklabels():
                        label.set_rotation(45)
                for line  in xaxis.get_ticklines(minor=True):
                        line.set_markersize(10)
                for line  in yaxis.get_ticklines(minor=True):
                        line.set_markersize(10)
                return True

        if mode == 'full':
                xaxis.set_major_locator(MultipleLocator(60))
                xaxis.set_major_formatter(FuncFormatter( formatter_x))
                for label in xaxis.get_ticklabels():
                        label.set_rotation(45)
                return True

        return False

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
        set_locator(mode, list_x, list_y)
        pyplot.subplots_adjust(bottom = 0.15)
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

def main(mode):
        x, y = read_file('a_%s.res' % mode)
        key_val = {}
        key_val['mode']         = mode
        key_val['list_x']       = x
        key_val['list_y']       = [int(item) for item in y]
        key_val['label_x']      = '时间(秒)'
        key_val['label_y']      = '人数(头)'
        key_val['name_title']   = '拍 牌 投 标'
        key_val['name_line']    = 'Number'
        key_val['name_file']    = ('a_%s.png' % mode)
        create_pic(key_val)       

if __name__ == '__main__':
        main('60')
        #main('full')

