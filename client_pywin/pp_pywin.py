#!/usr/bin/env python3

from tkinter            import Tk
from pickle             import dump, load
from traceback          import print_exc
from PIL                import Image, ImageTk
from io                 import BytesIO
from base64             import b64decode

from MainWin            import Console

from pp_log             import logger, printer
from pp_baseclass       import pp_sender

from pp_cmd             import proc_login, proc_image, proc_price

#===========================================================

class pp_client():
        def __init__(self, console, key_val):
                self.console    = console
                self.bidno      = key_val['bidno']
                self.passwd     = key_val['passwd']
                self.last_price = None
                self.sid        = None
                self.pid        = None
                self.udp        = None
                self.group      = 0

        def login_ok(self, key_val):
                if key_val == None:
                        return 

                self.pid = key_val['pid']                

                if self.udp != None :
                        self.udp.stop()

                arg_val = {}
                arg_val['bidno'] = self.bidno
                arg_val['pid']   = self.pid
                arg_val['group'] = self.group

                self.udp = udp_worker(self.console, arg_val)
                self.udp.start()
                self.udp.wait_for_start()
                self.udp.format_udp()

                self.console.update_login_status(info_val['name'])

        def login(self, key_val):
                logger.debug(key_val.items())
                self.group = key_val['group']
                try:
                        info_val = proc_login(key_val)
                except:
                        print_exc()
                        return
                self.console.update_login_status(info_val['name'])

        def image(self, key_val):
                logger.debug(key_val.items())
                key_val['bidno'] = self.bidno
                key_val['group'] = self.group
                try:
                        info_val = proc_image(key_val)
                except:
                        print_exc()
                        return
                price = key_val['price']
                self.last_price = price
                self.console.update_last_price(price)
                self.sid = info_val['sid']
                self.console.update_image_decode(info_val['image'])

        def price(self, key_val):
                logger.debug(key_val.items())
                key_val['bidno'] = self.bidno
                key_val['price'] = self.last_price
                key_val['passwd']= self.passwd
                key_val['sid']   = self.sid
                key_val['group'] = self.group
                try:
                        info_val = proc_price(key_val)
                except:
                        print_exc()
                        return
                self.console.update_first_price(info_val['price'])

        def logout(self, key_val):
                logger.debug(key_val.items())

#===========================================================

class cmd_proc(pp_sender):

        def __init__(self, console):
                self.func_dict =     {
                        'logout':               self.proc_logout,
                        'login':                self.proc_login,
                        'adjust_channel':       self.proc_adjust_channel,
                        'image_price':          self.proc_image_price,
                        'image_decode':         self.proc_image_decode,
                        }

                pp_sender.__init__(self)
                self.console = console
                self.client  = None

        def proc(self, key_val):
                try:
                        func = self.func_dict[key_val['cmd']]
                except KeyError:
                        logger.error('unknow cmd : %s ' % key_val['cmd'])
                else:
                        func(key_val)

        def proc_adjust_channel(self, key_val):
                logger.debug(key_val.items())

        def proc_logout(self, key_val):
                if self.client != None :
                        self.client.logout(key_val)

        def proc_login(self, key_val):
                if self.client == None :
                        self.client = pp_client(self.console, key_val)
                if self.client != None :
                        self.client.login(key_val)

        def proc_image_price(self, key_val):
                if self.client != None :
                        self.client.image(key_val)

        def proc_image_decode(self, key_val):
                if self.client != None :
                        self.client.price(key_val)

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
                key_val['price']  = self.input_image_price.get()
                #logger.debug(sorted(key_val.items()))
                self.cmd_proc.put(key_val)

        def proc_image_decode(self,p1):
                key_val = {}
                key_val['cmd']    = 'image_decode'
                key_val['image']  = self.input_image_decode.get()
                #logger.debug(sorted(key_val.items()))
                self.cmd_proc.put(key_val)

        #-------------------------------------
        # 回调接口
        #-------------------------------------

        def update_login_status(self, info):
                self.output_login_status['text'] = info
                self.output_login_status.update_idletasks()

        '''
        def update_change_time(self, info):
                self.output_change_time['text']   = info
                self.output_change_time.update_idletasks()

        def update_system_time(self, info):
                self.output_system_time['text']   = info
                self.output_system_time.update_idletasks()

        def update_current_price(self, info):
                self.output_current_price['text'] = info
                self.output_current_price.update_idletasks()
        '''

        def update_udp_info(self, ctime, stime, price):
                self.output_current_price['text'] = price
                self.output_system_time['text']   = stime
                self.output_change_time['text']   = ctime
                self.output_current_price.update_idletasks()
                self.output_system_time.update_idletasks()
                self.output_change_time.update_idletasks()

        def update_goal_channel(self, info):
                self.output_goal_channel['text'] = info
                self.output_goal_channel.update_idletasks()

        def update_current_channel(self, info):
                self.output_current_channel['text'] = info
                self.output_current_channel.update_idletasks()

        def update_first_price(self, info):
                self.output_first_price['text'] = info
                self.output_first_price.update_idletasks()

        def update_second_price(self, info):
                self.output_second_price['text'] = info
                self.output_second_price.update_idletasks()

        def update_third_price(self, info):
                self.output_third_price['text'] = info
                self.output_third_price.update_idletasks()

        def update_last_price(self, info):
                self.output_last_price['text'] = info
                self.output_last_price.update_idletasks()

        def update_image_decode(self, image):
                photo = ImageTk.PhotoImage(Image.open(BytesIO(b64decode(image))))
                self.output_image.image = photo
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
        Console (root)
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

