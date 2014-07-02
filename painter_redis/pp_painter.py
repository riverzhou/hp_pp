#!/usr/bin/env python3

from time               import sleep
from traceback          import print_exc
from queue              import Queue
from sys                import argv

from matplotlib.pyplot  import plot, legend, grid, draw, show, figure, subplots_adjust, gca, xlim, ylim, MultipleLocator, FuncFormatter

from pp_baseclass       import pp_sender
from pp_redis           import redis_parser

#=============================================================

MultipleLocator.MAXTICKS = 5000

#=============================================================

class data_info(pp_sender):
        def __init__(self, mode, info = ''):
                pp_sender.__init__(self, info)
                self.mode = mode

        def proc(self, buff):
                x, y, z = buff
                self.paint(x, y, z)

        def paint(self, x, y, z):
                global line1, list_z
                if len(x) == 0 or len(y) == 0 : return
                while line1 == None : sleep(1)
                list_z = z
                set_locator(self.mode, x, y)
                line1.set_xdata(x)
                line1.set_ydata(y)
                draw()

#=============================================================

def formatter_x(x, p):
        global list_z
        x = int(x+0.5)
        if x >= len(list_z) or x < 0 :
                return ''
        return list_z[x]

def set_locator(mode, list_x, list_y):
        xaxis = gca().xaxis
        yaxis = gca().yaxis

        if mode == 'B':
                xlim(int(min(list_x)), int(max(max(list_x),60)+1))
                ylim(int(min(list_y))-100, int(max(list_y))+300)
                xaxis.set_major_locator(MultipleLocator(1))
                xaxis.set_minor_locator(MultipleLocator(1))
                xaxis.set_major_formatter(FuncFormatter( formatter_x))
                yaxis.set_major_locator(MultipleLocator(100))
                for label in xaxis.get_ticklabels():
                        label.set_rotation(45)
                for line  in xaxis.get_ticklines(minor=True):
                        line.set_markersize(10)
                for line  in yaxis.get_ticklines(minor=True):
                        line.set_markersize(10)
                return True

        if mode == 'A':
                xlim(0, int(max(max(list_x),60)+1))
                ylim(0, int(max(list_y)))
                n = len(list_x) / 30
                n = int(n) if n > 1 else 1
                m = max(list_y) / (30*100)
                m = int(m) if m > 1 else 1
                m = m * 100
                xaxis.set_major_locator(MultipleLocator(n))
                xaxis.set_major_formatter(FuncFormatter(formatter_x))
                yaxis.set_major_locator(MultipleLocator(m))
                for label in xaxis.get_ticklabels():
                        label.set_rotation(45)
                return True

        return False

#=============================================================

line1 = None
def pic_draw():
        global line1

        x = [0,1]
        y = [0,1]

        figure(figsize = (16,9))
        line1 = plot(x,y,'r')[0]
        line1.axes.set_xlim(0, max(x))
        line1.axes.set_ylim(0, max(y))
        line1.set_label("line1")
        subplots_adjust(bottom = 0.15)
        #set_locator(mode, x, y)
        legend()
        grid()
        draw()
        show()

def main(mode):
        data_creater = data_info(mode)
        data_creater.start()
        data_creater.wait_for_start()
        data_parser  = redis_parser(mode, data_creater,'redis_parser')
        if data_parser == None : return
        data_parser.start()
        data_parser.wait_for_start()
        pic_draw()

def usage():
        print   (
                './pp_painter.py  A/B \n'+
                './pp_painter.py  a/b \n'
                )
        return False

def check_argv(argv):
        if len(argv) != 2              : return usage()
        mode = argv[1].upper()
        if mode != 'A' and mode != 'B' : return usage()
        return mode

#=============================================================

if __name__ == '__main__' :
        try:
                mode = check_argv(argv)
                if mode != False : main(mode)
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()
        finally:
                print()


