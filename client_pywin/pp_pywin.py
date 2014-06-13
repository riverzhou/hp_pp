#!/usr/bin/env python3

from tkinter            import Tk
from pickle             import dump, load
from traceback          import print_exc
from PIL                import Image, ImageTk
from io                 import BytesIO
from base64             import b64decode

from MainWin            import Console, GEOMETRY

from pp_log             import logger, printer
from pp_baseclass       import pp_sender

#===========================================================

class cmd_proc(pp_sender):
        def __init__(self, console):
                pp_sender.__init__(self)
                self.console = console

        def proc(self, key_val):
                logger.debug('cmd_proc : ' + key_val['cmd'])
                logger.debug(sorted(key_val.items()))


class Console(Console):
        def __init__(self, master=None):
                super(Console, self).__init__(master)
                self.load_database()
                self.cmd_proc = cmd_proc(self)
                self.cmd_proc.start()
                self.cmd_proc.wait_for_start()

        def load_database(self):
                global database
                if not hasattr(database, 'db') :
                        return

                bidno       = database.db['bidno']       if 'bidno'       in database.db else ''
                passwd      = database.db['passwd']      if 'passwd'      in database.db else ''

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

        def proc_login(self,p1):
                key_val = {}
                key_val['cmd']    = 'login'
                key_val['bidno']  = self.input_bidno.get()
                key_val['passwd'] = self.input_passwd.get()
                key_val['group']  = self.var_use_group2.get()
                #logger.debug(sorted(key_val.items()))
                self.cmd_proc.put(key_val)

                db ={}
                db['bidno']    = key_val['bidno']
                db['passwd']   = key_val['passwd']
                self.save_database(db)

        def proc_channel(self,p1):
                key_val = {}
                key_val['cmd']    = 'adjust_channel'
                key_val['size']   = self.input_ajust_channel.get()
                #logger.debug(sorted(key_val.items()))
                self.cmd_proc.put(key_val)

        def proc_image_price(self,p1):
                key_val = {}
                key_val['cmd']    = 'image_price'
                key_val['price'] = self.input_image_price.get()
                #logger.debug(sorted(key_val.items()))
                self.cmd_proc.put(key_val)

        def proc_image_decode(self,p1):
                key_val = {}
                key_val['cmd']    = 'image_decode'
                key_val['number'] = self.input_image_decode.get()
                #logger.debug(sorted(key_val.items()))
                self.cmd_proc.put(key_val)

        #-------------------------------------
        # 回调接口
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

def pp_init_tk():
        root = Tk()
        root.title('Console')
        root.geometry(GEOMETRY)
        win  = Console (root)
        root.mainloop()

def pp_main():
        logger.info('Client Started ...')
        pp_init_tk()

#-----------------------------------------------------------

if __name__ == '__main__':
        load_dump()
        try:
                pp_main()
        except KeyboardInterrupt:
                pass
        save_dump()
