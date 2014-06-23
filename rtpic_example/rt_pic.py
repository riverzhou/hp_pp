#!/usr/bin/env python3

from time       import sleep
from traceback  import print_exc
from queue      import Queue
from threading  import Thread

from matplotlib.pyplot import ion, ioff, plot, legend, grid, draw, show, figure, subplots_adjust

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

line1 = None
def pic_draw():
        global line1

        x = [0]
        y = [0]

        figure(figsize = (16,9))
        line1 = plot(x,y,'r')[0]
        line1.axes.set_xlim(min(x), max(x))
        line1.axes.set_ylim(min(y), max(y))
        line1.set_label("line1")
        subplots_adjust(bottom = 0.15)
        legend()
        grid()
        draw()
        show()

class data_creater(Thread):
        def run(self):
                global line1
                i = 0
                x = []
                y = []
                key_val = {}

                while True:
                        if line1 == None:
                                sleep(1)
                                continue
                        x.append(i)
                        y.append(i*i)

                        #if len(x) >= 10 : del(x[0])
                        #if len(y) >= 10 : del(y[0])

                        #print(x,y)

                        line1.set_xdata(x)
                        line1.set_ydata(y)
                        line1.axes.set_xlim(min(x), max(x))
                        line1.axes.set_ylim(min(y), max(y))
                        draw()

                        i += 100
                        if i > 5000 : break
                        sleep(0.1)


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


