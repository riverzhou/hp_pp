#!/usr/bin/env python3

from tkinter            import Tk
from pickle             import dump, load
from traceback          import print_exc
from PIL                import Image, ImageTk
from io                 import BytesIO
from base64             import b64decode

from pp_log             import logger, printer
from pp_baseclass       import pp_sender
from pp_udpworker       import udp_worker
from pp_sslproto        import proto_machine
from pp_sslworker       import proc_ssl_login, proc_ssl_toubiao
from MainWin            import Console

#===========================================================

class pp_client():
        def __init__(self, console, key_val):
                self.console                    = console
                self.machine                    = proto_machine()
                self.udp                        = None

                self.info_val                   = {}
                self.info_val['bidno']          = key_val['bidno']
                self.info_val['passwd']         = key_val['passwd']
                self.info_val['mcode']          = self.machine.mcode
                self.info_val['login_image']    = self.machine.image
                self.info_val['last_price']     = 0
                self.info_val['sid']            = None
                self.info_val['pid']            = None
                self.info_val['group']          = 0

        def stop_udp(self):
                if self.udp != None :           return self.udp.stop()

        def login_ok(self, key_val):
                if key_val == None :            return
                if 'errcode' in key_val :       return

                self.info_val['pid']            = key_val['pid']

                self.stop_udp()
                self.udp = udp_worker(self.console, self.info_val)
                self.udp.start()
                self.udp.wait_for_start()
                self.udp.format_udp()

                self.console.update_login_status(key_val['name'])

        def login(self, key_val):
                self.info_val['group']          = key_val['group']
                try:
                        return proc_ssl_login.send('login', self.info_val, self.login_ok)
                except:
                        print_exc()

        def image_ok(self, key_val):
                if key_val == None :            return
                if 'errcode' in key_val :       return
                if key_val['image'] == None :   return

                self.info_val['sid']            = key_val['sid']
                self.info_val['last_price']     = key_val['price']

                self.console.update_image_decode(key_val['image'], self.info_val['last_price'])

        def image(self, key_val):
                self.info_val['image_price']    = key_val['price']
                try:
                        return proc_ssl_toubiao.send('image', self.info_val, self.image_ok)
                except:
                        print_exc()

        def price_ok(self, key_val):
                if key_val == None :            return
                if 'errcode' in key_val :       return

                count = key_val['count']
                if count == '1' : return self.console.update_first_price(key_val['price'])
                if count == '2' : return self.console.update_second_price(key_val['price'])
                if count == '3' : return self.console.update_third_price(key_val['price'])
                logger.error('price count error %s' % count)

        def price(self, key_val):
                self.info_val['shot_price']     = self.info_val['last_price']
                self.info_val['image_decode']   = key_val['image']
                try:
                        return proc_ssl_toubiao.send('price', self.info_val, self.price_ok)
                except:
                        print_exc()

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
                        return
                try:
                        func(key_val)
                except:
                        print_exc()

        def proc_adjust_channel(self, key_val):
                logger.debug(key_val.items())

        def proc_logout(self, key_val):
                if self.client != None :
                        self.client.logout(key_val)

        def proc_login(self, key_val):
                if   self.client == None :
                        self.client = pp_client(self.console, key_val)
                elif self.client.info_val['bidno'] != key_val['bidno'] or self.client.info_val['passwd'] != key_val['passwd']:
                        self.client.stop_udp()
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
                if key_val['bidno'] == '' or key_val['passwd'] == '' :  return
                self.cmd_proc.put(key_val)

                db ={}
                db['bidno']       = key_val['bidno']
                db['passwd']      = key_val['passwd']
                self.save_database(db)

        def proc_channel(self,p1):
                key_val = {}
                key_val['cmd']    = 'adjust_channel'
                key_val['size']   = self.input_ajust_channel.get()
                if key_val['size'] == '' :      return
                self.cmd_proc.put(key_val)

        def proc_image_price(self,p1):
                key_val = {}
                key_val['cmd']    = 'image_price'
                key_val['price']  = self.input_image_price.get()
                if key_val['price'] == '' :     return
                self.cmd_proc.put(key_val)

        def proc_image_decode(self,p1):
                key_val = {}
                key_val['cmd']    = 'image_decode'
                key_val['image']  = self.input_image_decode.get()
                if key_val['image'] == '' :     return
                self.cmd_proc.put(key_val)

        #-------------------------------------
        # 回调接口
        #-------------------------------------

        def update_login_status(self, info):
                self.output_login_status['text']    = info
                self.output_login_status.update_idletasks()

        def update_udp_info(self, ctime, stime, price):
                self.output_current_price['text']   = price
                self.output_system_time['text']     = stime
                self.output_change_time['text']     = ctime
                self.output_current_price.update_idletasks()
                self.output_system_time.update_idletasks()
                self.output_change_time.update_idletasks()

        def update_goal_channel(self, info):
                self.output_goal_channel['text']    = info
                self.output_goal_channel.update_idletasks()

        def update_current_channel(self, info):
                self.output_current_channel['text'] = info
                self.output_current_channel.update_idletasks()

        def update_first_price(self, info):
                self.output_first_price['text']     = info
                self.output_first_price.update_idletasks()

        def update_second_price(self, info):
                self.output_second_price['text']    = info
                self.output_second_price.update_idletasks()

        def update_third_price(self, info):
                self.output_third_price['text']     = info
                self.output_third_price.update_idletasks()

        def update_image_decode(self, image, price):
                try:
                        image = b64decode(image)
                        photo = ImageTk.PhotoImage(Image.open(BytesIO(image)))
                except:
                        global err_jpg
                        self.output_image.image     = err_jpg
                        self.output_image['image']  = err_jpg
                        self.output_image.update_idletasks()
                        self.save_jpg(image)
                        logger.error('图片错误，重新请求')
                else:
                        self.output_image.image     = photo
                        self.output_image['image']  = photo
                        self.output_image.update_idletasks()
                        self.output_last_price['text']  = price
                        self.output_last_price.update_idletasks()

        def save_jpg(self,jpg):
                f = open('bad.jpg','wb')
                f.write(jpg)
                f.close()

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

def tk_init_err():
        global err_jpg
        f = open('err.jpg', 'rb')
        err_jpg = ImageTk.PhotoImage(Image.open(f))
        f.close()

def pp_init_tk():
        root = Tk()
        tk_init_err()
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

