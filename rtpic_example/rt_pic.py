#!/usr/bin/env python3

from time       import sleep
from traceback  import print_exc
from queue      import Queue
from threading  import Thread

from matplotlib.pyplot import ion, ioff, plot, legend, grid, draw, show, figure

Thread.daemon = True

class data_info():
        def __init__(self):
                self.queue = Queue()

        def put(self, key_val):
                self.queue.put(key_val)

        def get(self):
                try:
                        info = self.queue.get()
                except KeyboardInterrupt:
                        return None
                except:
                        print_exc()
                        return None
                else:
                        return info

data_pic  = data_info()

def pic_draw():
        ion()

        x = [0,1]
        y = [0,1]

        figure(figsize = (16,9))
        line1 = plot(x,y,'r')[0]
        line1.axes.set_xlim(min(x), max(x))
        line1.axes.set_ylim(min(y), max(y))
        line1.set_label("line1")
        legend()
        grid()
        draw()

        while True:
                global data_pic
                key_val = data_pic.get()
                if key_val == None : break
                x = key_val['x']
                y = key_val['y']
                line1.set_xdata(x)
                line1.set_ydata(y)
                line1.axes.set_xlim(min(x), max(x))
                line1.axes.set_ylim(min(y), max(y))
                draw()

        ioff()
        show()

class data_creater(Thread):
        def run(self):
                global data_pic
                i = 0
                x = []
                y = []
                key_val = {}

                while True:
                        x.append(i)
                        y.append(i)
                        key_val['x'] = x
                        key_val['y'] = y
                        data_pic.put(key_val)
                        i += 100
                        if i > 2000 : break
                        sleep(1)

                data_pic.put(None)


def main():
        creater = data_creater()
        creater.start()
        pic_draw()

if __name__ == '__main__' :

        try:
                main()
        except KeyboardInterrupt:
                pass
        except:
                print_exc()

