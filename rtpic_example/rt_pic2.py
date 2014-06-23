#!/usr/bin/env python3

from tkinter    import Tk, Label
from PIL        import Image, ImageTk
from io         import BytesIO
from time       import sleep
from threading  import Thread
Thread.daemon = True

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#=====================================================================

class pic_creater(Thread):
        def __init__(self):
                Thread.__init__(self)
                self.buf = BytesIO()
                self.flag_init = False

        def run(self):
                #plt.figure()
                plt.title("test")
                i = 0
                x = []
                y = []
                line = plt.plot(x, y, 'r')[0]
                while True:
                        x.append(i)
                        y.append(i*i)

                        #if len(x) >= 10 : del(x[0])
                        #if len(y) >= 10 : del(y[0])

                        line.set_xdata(x)
                        line.set_ydata(y)
                        line.axes.set_xlim(min(x), max(x))
                        line.axes.set_ylim(min(y), max(y))

                        self.buf.seek(0)
                        plt.savefig(self.buf, format = 'png')
                        self.buf.seek(0)
                        self.pic_draw()

                        i += 100
                        if i > 5000 : break
                        sleep(0.1)

        def pic_draw(self):
                global label
                if label == None : return None
                photo = ImageTk.PhotoImage(file=self.buf, format='png')
                label.image = photo
                label["image"] = photo
                if self.flag_init != True :
                        label.pack()
                        self.flag_init = True
                label.update_idletasks()
                return True

label = None
def tk_create():
        global label
        root  = Tk()
        root.title('Image')
        label = Label()
        #label.pack()
        root.mainloop()
        label = None

if __name__ == '__main__':
        creater = pic_creater()
        creater.start()
        tk_create()

