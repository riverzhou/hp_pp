#!/usr/bin/env python3

from tkinter    import Tk 
from pickle     import dump, load
from traceback  import print_exc
from PIL        import Image, ImageTk
from io         import BytesIO
from base64     import b64decode

from MainWin    import Console, GEOMETRY

from pp_log     import logger, printer
from pp_thread  import cmd_sender
from ct_proto   import ctrl_ct
from pr_proto   import ctrl_pr

#===========================================================

class Console(Console):
        def __init__(self, master=None):
                global daemon_ct, daemon_pr
                super(Console, self).__init__(master)
                self.load_database()
                daemon_pr.reg(self)
                daemon_ct.reg(self)
                self.cmd_sender = cmd_sender(daemon_ct)
                self.cmd_sender.start()
                self.cmd_sender.started()

        def load_database(self):
                global database
                if not hasattr(database, 'db') :
                        return

                server_ip   = database.db['server_ip']   if 'server_ip'   in database.db else ''
                server_port = database.db['server_port'] if 'server_port' in database.db else ''
                bidno       = database.db['bidno']       if 'bidno'       in database.db else ''
                passwd      = database.db['passwd']      if 'passwd'      in database.db else ''

                self.input_ip.insert(0, server_ip)
                self.input_port.insert(0, server_port)
                self.input_bidno.insert(0, bidno)
                self.input_passwd.insert(0, passwd)

        def save_database(self, key_val):
                global database
                if not hasattr(database, 'db') :
                        database.db = {}
                for key in key_val:
                        database.db[key] = key_val[key]

        #-------------------------------------
        # 按钮触发处理
        #-------------------------------------

        def button_image_warmup_clicked(self, event):
                key_val = {}
                key_val['cmd']    = 'image_warmup'
                key_val['bidid']  = '1'
                self.cmd_sender.send(key_val)
                print(sorted(key_val.items()))

        def button_price_warmup_clicked(self, event):
                key_val = {}
                key_val['cmd']    = 'price_warmup'
                key_val['bidid']  = '1'
                self.cmd_sender.send(key_val)
                print(sorted(key_val.items()))

        def button_image_price_clicked(self, event):
                key_val = {}
                key_val['cmd']    = 'image_shoot'
                key_val['bidid']  = '1'
                key_val['price']  = self.input_image_price.get()
                self.cmd_sender.send(key_val)
                print(sorted(key_val.items()))

        def button_image_number_clicked(self, event):
                key_val = {}
                key_val['cmd']    = 'image_decode'
                key_val['bidid']  = '1'
                key_val['number'] = self.input_image_number.get()
                self.cmd_sender.send(key_val)
                print(sorted(key_val.items()))

        def button_connect_clicked(self, event):
                addr = (self.input_ip.get(), int(self.input_port.get()))
                print(addr)
                daemon_pr.connect(addr)
                daemon_ct.connect(addr)
                daemon_pr.wait_for_connect()
                daemon_ct.wait_for_connect()
                key_val = {}
                key_val['cmd']    = 'login'
                key_val['bidno']  = self.input_bidno.get()
                key_val['passwd'] = self.input_passwd.get()
                print(sorted(key_val.items()))
                self.cmd_sender.send(key_val)

                db ={}
                db['server_ip']   = addr[0]
                db['server_port'] = str(addr[1])
                db['bidno']    = key_val['bidno']
                db['passwd']   = key_val['passwd']
                self.save_database(db)

        #-------------------------------------
        # sock 回调接口
        #-------------------------------------

        def update_info(self, key_val):
                print(sorted(key_val.items()))

        def update_price_warmup(self, key_val):
                pass

        def update_image_warmup(self, key_val):
                pass

        def update_image_shoot(self, key_val):
                pass

        def update_image_decode(self, key_val):
                image = key_val['image']
                photo = ImageTk.PhotoImage(Image.open(BytesIO(b64decode(image)))) 
                self.output_image['image'] = photo
                self.output_image.update_idletasks()

#===========================================================

class DataBase():
        pass

database = DataBase()
db_name  = 'pp_db.dump'

#-----------------------------------------------------------

def load_dump():
        global db_name, database
        try:
                f = open(db_name, 'rb')
                database = load(f)
                f.close()
                logger.info('DataBase Loaded')
                print(database.db)
        except FileNotFoundError:
                database.db = {}
                logger.info('DataBase Created')
        except:
                print_exc()


def save_dump():
        global db_name, database
        try:
                f = open(db_name, 'wb')
                dump(database, f, 4)
                f.close()
                logger.info('DataBase Saved')
                print(database.db)
        except:
                print_exc()

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

#-----------------------------------------------------------

if __name__ == '__main__':
        load_dump()
        try:
                ct_main()
        except KeyboardInterrupt:
                pass
        save_dump()

