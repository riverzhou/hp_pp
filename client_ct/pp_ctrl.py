#!/usr/bin/env python3

from tkinter import Tk, Toplevel

from MainWin import Console, GEOMETRY

from pp_log  import logger, printer

from pp_thread                  import pp_subthread, cmd_sender
from ct_proto                   import ctrl_ct
from pr_proto                   import ctrl_pr 
from pp_db                      import *


#===========================================================
#-----------------------------------------------------------

class Console(Console):
        def __init__(self, master=None):
                global daemon_ct, daemon_pr
                super(Console, self).__init__(master)
                daemon_pr.reg(self)
                daemon_ct.reg(self)
                self.cmd_sender = cmd_sender(daemon_ct)
                self.cmd_sender.start()
                self.cmd_sender.started()

        def button_image_warmup_clicked(self, event):
                key_val = {}
                key_val['cmd']    = 'image_warmup'
                self.cmd_sender.send(key_val)
                print(sorted(key_val.items()))

        def button_price_warmup_clicked(self, event):
                key_val = {}
                key_val['cmd']    = 'price_warmup'
                self.cmd_sender.send(key_val)
                print(sorted(key_val.items()))

        def button_image_price_clicked(self, event):
                key_val = {}
                key_val['cmd']    = 'image_price'
                key_val['price']  = self.get_input_image_price()
                self.cmd_sender.send(key_val)
                print(sorted(key_val.items()))

        def button_image_number_clicked(self, event):
                key_val = {}
                key_val['cmd']    = 'image_number'
                key_val['number'] = self.get_input_image_number()
                self.cmd_sender.send(key_val)
                print(sorted(key_val.items()))

        def button_connect_clicked(self, event):
                addr = (self.get_input_ip(), int(self.get_input_port()))
                print(addr)
                daemon_pr.connect(addr)
                daemon_ct.connect(addr)
                daemon_pr.wait_for_connect()
                daemon_ct.wait_for_connect()
                key_val = {}
                key_val['cmd']    = 'login'
                key_val['bidno']  = self.get_input_bidno()
                key_val['passwd'] = self.get_input_passwd()
                print(sorted(key_val.items()))
                self.cmd_sender.send(key_val)

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

        def update_info(self, key_val):
                print(sorted(key_val.items()))

        def update_price_warmup(self, key_val):
                pass

        def update_image_warmup(self, key_val):
                pass

        def update_image_shoot(self, key_val):
                pass

        def update_image_decode(self, key_val):
                pass

#===========================================================

def ct_init_pr():
        global daemon_pr
        daemon_pr = ctrl_pr()
        daemon_pr.start()
        daemon_pr.started()

def ct_init_ct():
        global daemon_ct
        daemon_ct = ctrl_ct()
        daemon_ct.start()
        daemon_ct.started()

def ct_init_tk():
        root = Tk()
        root.title('Console')
        root.geometry(GEOMETRY)
        win  = Console (root)
        root.mainloop()

def ct_main():
        ct_init_pr()
        ct_init_ct()
        logger.info('Client Started ...')
        ct_init_tk()

if __name__ == '__main__':
        load_dump()
        try:
                ct_main()
        except KeyboardInterrupt:
                pass
        save_dump()

