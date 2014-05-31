#!/usr/bin/env python3

from tkinter import Tk, Toplevel

from MainWin import Console, GEOMETRY

from pp_log  import logger, printer


class Console(Console):
        def __init__(self, master=None):
                super(Console, self).__init__(master)

        def button_image_warmup_clicked(self, event):
                print('button_image_warmup_clicked')

        def button_price_warmup_clicked(self, event):
                print('button_price_warmup_clicked')

        def button_image_price_clicked(self, event):
                print('button_image_price_clicked')

        def button_image_number_clicked(self, event):
                print('button_image_number_clicked')

        def button_connect_clicked(self, event):
                ip   = self.get_input_ip()
                port = self.get_input_port()
                addr = (ip, port)
                print(addr)

        def get_input_ip(self):
                return self.input_ip.get()

        def get_input_port(self):
                return self.input_port.get()

        def get_input_bidno(self):
                return self.input_bidno.get()

        def get_input_passwd(self):
                return self.input_passwd.get()

        def get_input_image_price(self):
                return self.input_image_price.get()

        def get_input_image_number(self):
                return self.input_image_number.get()


if __name__ == '__main__':
        root = Tk()
        root.title('Console')
        root.geometry(GEOMETRY)
        win  = Console (root)
        root.mainloop()
   
