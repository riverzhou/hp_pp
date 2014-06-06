#!/usr/bin/env python3

import numpy 
from   matplotlib           import pyplot, font_manager
from   matplotlib.ticker    import MultipleLocator, FuncFormatter

plfonts = font_manager.FontProperties(fname='./msyh.ttf')

def formatter_x(x, p):
        global list_x
        x = int(x)
        if x >= len(list_x) or x < 0 : 
                return ''
        return list_x[x]

def create_pic(key_val):
        global list_x
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
        pyplot.ylim(int(min(list_y)), int(max(list_y))+300)
        pyplot.subplots_adjust(bottom = 0.15)
        #pyplot.gca().xaxis.set_major_locator(MultipleLocator(max(int(len(list_x)/15),1)))
        pyplot.gca().xaxis.set_major_locator(MultipleLocator(1))
        pyplot.gca().xaxis.set_minor_locator(MultipleLocator(1))
        pyplot.gca().xaxis.set_major_formatter(FuncFormatter( formatter_x))
        #pyplot.gca().yaxis.set_major_locator(MultipleLocator(max(int(int((int(max(list_y))-int(min(list_y)))/len(list_x))/100)*100, 100)))
        pyplot.gca().yaxis.set_major_locator(MultipleLocator(100))
        pyplot.gca().yaxis.set_minor_locator(MultipleLocator(100))
        for label in pyplot.gca().xaxis.get_ticklabels():
                label.set_rotation(45)
        for line  in pyplot.gca().xaxis.get_ticklines(minor=True):
                line.set_markersize(10)
        for line  in pyplot.gca().yaxis.get_ticklines(minor=True):
                line.set_markersize(10)
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

def main():
        x, y = read_file('a.res')
        key_val = {}
        key_val['list_x']       = x
        key_val['list_y']       = y
        key_val['label_x']      = '时间(秒)'
        key_val['label_y']      = '价格(元)'
        key_val['name_title']   = '拍 牌 投 标'
        key_val['name_line']    = 'Price'
        key_val['name_file']    = 'price.png'
        create_pic(key_val)       

if __name__ == '__main__':
        main()

