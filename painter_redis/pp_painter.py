#!/usr/bin/env python3

from time               import sleep
from traceback          import print_exc
from queue              import Queue
from sys                import argv

from matplotlib.pyplot  import plot, legend, grid, draw, show, figure, subplots_adjust

from pp_baseclass       import pp_sender
from pp_readredis       import redis_parser

class data_info(pp_sender):
        def __init__(self, mode, info = ''):
                pp_sender.__init__(self, info)
                self.mode = mode

        def proc(self, buff):
                x, y, z = buff
                self.paint(x, y, z)

        def paint(self, x, y, z):
                global line1
                if len(x) == 0 or len(y) == 0 : return
                while line1 == None : sleep(1)
                line1.set_xdata(x)
                line1.set_ydata(y)
                line1.axes.set_xlim(min(x), max(x))
                line1.axes.set_ylim(min(y), max(y))
                draw()

#=============================================================

line1 = None
def pic_draw():
        global line1

        x = [0,1]
        y = [0,1]

        figure(figsize = (16,9))
        line1 = plot(x,y,'r')[0]
        line1.axes.set_xlim(min(x), max(x))
        line1.axes.set_ylim(min(y), max(y))
        line1.set_label("line1")
        subplots_adjust(bottom = 0.15)
        #set_locator(mode, list_x, list_y)
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


