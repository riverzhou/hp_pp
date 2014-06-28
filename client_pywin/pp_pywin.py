#!/usr/bin/env python3

from tkinter            import Tk
from pickle             import dump, load
from traceback          import print_exc
from PIL                import Image, ImageTk
from io                 import BytesIO
from base64             import b64decode
from threading          import Event, Lock

from pp_log             import logger, printer
from pp_baseclass       import pp_sender
from pp_udpworker       import udp_worker
from pp_sslproto        import proto_machine
from pp_sslworker       import proc_ssl_login, proc_ssl_image, proc_ssl_price
from MainWin            import Console

#===========================================================

class pp_udp():
        def __init__(self, console, commander, key_val):
                self.console                    = console
                self.commander                  = commander
                self.udp                        = [None, None]
                self.info_val                   = {}
                self.info_val['udp_bidno']      = key_val['udp_bidno']
                self.info_val['udp_pid']        = key_val['udp_pid']

        def login(self, key_val):
                self.stop()

                arg_val = ({},{})

                arg_val[0]['bidno'] = self.info_val['udp_bidno']
                arg_val[0]['pid']   = self.info_val['udp_pid']
                arg_val[0]['group'] = 0

                arg_val[1]['bidno'] = self.info_val['udp_bidno']
                arg_val[1]['pid']   = self.info_val['udp_pid']
                arg_val[1]['group'] = 1

                self.udp[0] = udp_worker(self.console, arg_val[0])
                self.udp[1] = udp_worker(self.console, arg_val[1])

                self.start()

        def reg(self, price_shot, event_shot):
                self.udp[0].reg(price_shot, event_shot)
                self.udp[1].reg(price_shot, event_shot)

        def start(self):
                if self.udp[0] != None :        self.udp[0].start()
                if self.udp[1] != None :        self.udp[1].start()

        def stop(self):
                if self.udp[0] != None :        self.udp[0].stop()
                if self.udp[1] != None :        self.udp[1].stop()
                self.udp[0] = None
                self.udp[1] = None

class pp_client():
        def __init__(self, console, commander, key_val):
                self.console                    = console
                self.commander                  = commander
                self.machine                    = proto_machine()
                self.udp                        = None
                self.udp2                       = None
                self.info_val                   = {}
                self.info_val['bidno']          = key_val['bidno']
                self.info_val['passwd']         = key_val['passwd']
                self.info_val['mcode']          = self.machine.mcode
                self.info_val['login_image']    = self.machine.image
                self.info_val['last_price']     = 0
                self.info_val['sid']            = None
                self.info_val['pid']            = None
                self.info_val['group']          = 0
                self.event_shot                 = Event()
                self.onway_price_worker         = [0,0]
                self.lock_price_worker          = Lock()
                self.lock_login_cb              = Lock()
                self.lock_image_cb              = Lock()

        def price_worker_in(self, group):
                worker = [0,0]
                self.lock_price_worker.acquire()
                if group == 0 :
                        self.onway_price_worker[0] += 1
                elif group == 1:
                        self.onway_price_worker[1] += 1
                else:
                        pass
                worker[0] = self.onway_price_worker[0]
                worker[1] = self.onway_price_worker[1]
                self.lock_price_worker.release()
                self.console.update_price_worker('%.2d : %.2d' % (worker[0], worker[1]))

        def price_worker_out(self, group):
                worker = [0,0]
                self.lock_price_worker.acquire()
                if group == 0 :
                        self.onway_price_worker[0] -= 1
                elif group == 1:
                        self.onway_price_worker[1] -= 1
                else:
                        pass
                worker[0] = self.onway_price_worker[0]
                worker[1] = self.onway_price_worker[1]
                self.lock_price_worker.release()
                self.console.update_price_worker('%.2d : %.2d' % (worker[0], worker[1]))

        def login_ok(self, key_val):
                if key_val == None :            return
                if 'errcode' in key_val :
                        logger.error('login error! errcode %s , errstring %s' % (key_val['errcode'], key_val['errstring']))
                        return

                self.lock_login_cb.acquire()
                self.info_val['pid'] = key_val['pid']
                udp_bidno = self.info_val['bidno']
                udp_pid   = self.info_val['pid']
                self.lock_login_cb.release()

                self.console.update_login_status(key_val['name'])
                self.console.update_udp_input(udp_bidno, udp_pid)

        def login(self, key_val):
                global proc_ssl_login
                self.info_val['group']          = key_val['group']
                try:
                        arg_val = {}
                        for key in self.info_val :
                                arg_val[key]    = self.info_val[key]
                        proc_ssl_login.send(arg_val, self.login_ok)
                except:
                        print_exc()

        def image_ok(self, key_val):
                if key_val == None :            return
                if 'errcode' in key_val :
                        logger.error('image error! errcode %s , errstring %s' % (key_val['errcode'], key_val['errstring']))
                        return
                if key_val['image'] == None :
                        logger.error('image error! image decode failed')
                        return

                self.lock_image_cb.acquire()
                self.info_val['sid']            = key_val['sid']
                self.info_val['last_price']     = key_val['price']
                self.lock_image_cb.release()

                self.console.update_image_decode(key_val['image'], self.info_val['last_price'])

        def image(self, key_val):
                global proc_ssl_image
                self.info_val['image_price']    = key_val['price']
                self.info_val['group']          = key_val['group']
                try:
                        arg_val = {}
                        for key in self.info_val :
                                arg_val[key]    = self.info_val[key]
                        proc_ssl_image.send(arg_val, self.image_ok)
                except:
                        print_exc()

        def price_ok(self, key_val):
                if key_val == None :            return
                if 'errcode' in key_val :
                        logger.error('price error! errcode %s , errstring %s' % (key_val['errcode'], key_val['errstring']))
                        return

                count = key_val['count']
                if count == '1' : return self.console.update_first_price(key_val['price'])
                if count == '2' : return self.console.update_second_price(key_val['price'])
                if count == '3' : return self.console.update_third_price(key_val['price'])
                logger.error('price count error %s' % count)

        def price(self, key_val):
                global proc_ssl_price
                self.info_val['shot_price']     = self.info_val['last_price']
                self.info_val['image_decode']   = key_val['image']
                self.event_shot.clear()
                if self.commander.udp != None : 
                        self.commander.udp.reg(self.info_val['shot_price'], self.event_shot)
                else:
                        logger.error('commander.udp == None')
                try:
                        arg_val = {}
                        for key in self.info_val :
                                arg_val[key]    = self.info_val[key]
                        arg_val['event']        = self.event_shot
                        arg_val['delay']        = 0
                        arg_val['worker_in']    = self.price_worker_in
                        arg_val['worker_out']   = self.price_worker_out
                        proc_ssl_price.send(arg_val, self.price_ok)
                except:
                        print_exc()
                try:
                        arg_val = {}
                        for key in self.info_val :
                                arg_val[key]    = self.info_val[key]
                        arg_val['event']        = self.event_shot
                        arg_val['delay']        = 1
                        arg_val['worker_in']    = self.price_worker_in
                        arg_val['worker_out']   = self.price_worker_out
                        proc_ssl_price.send(arg_val, self.price_ok)
                except:
                        print_exc()

        def logout(self, key_val):
                logger.debug(key_val.items())

#===========================================================

class cmd_proc(pp_sender):
        def __init__(self, console):
                self.func_dict =     {
                        'logout':               self.proc_logout,
                        'ssl_login':            self.proc_ssl_login,
                        'udp_login':            self.proc_udp_login,
                        'image_channel_connect':self.proc_image_channel_connect,
                        'price_channel_connect':self.proc_price_channel_connect,
                        'image_channel_stop':   self.proc_image_channel_stop,
                        'price_channel_stop':   self.proc_price_channel_stop,
                        'image_channel':        self.proc_image_channel,
                        'price_channel':        self.proc_price_channel,
                        'image_price':          self.proc_image_price,
                        'image_decode':         self.proc_image_decode,
                        }
                pp_sender.__init__(self)
                self.console = console
                self.client  = None
                self.udp     = None

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

        def proc_image_channel_connect(self, key_val):
                global proc_ssl_image
                proc_ssl_image.set_pool_start()

        def proc_price_channel_connect(self, key_val):
                global proc_ssl_price
                proc_ssl_price.set_pool_start()

        def proc_image_channel_stop(self, key_val):
                global proc_ssl_image
                proc_ssl_image.set_pool_stop()

        def proc_price_channel_stop(self, key_val):
                global proc_ssl_price
                proc_ssl_price.set_pool_stop()

        def proc_image_channel(self, key_val):
                global proc_ssl_image
                proc_ssl_image.set_pool_size(int(key_val['size']))

        def proc_price_channel(self, key_val):
                global proc_ssl_price
                proc_ssl_price.set_pool_size(int(key_val['size']))

        def proc_logout(self, key_val):
                if self.client != None :
                        self.client.logout(key_val)

        def proc_ssl_login(self, key_val):
                if self.client == None :
                        self.client = pp_client(self.console, self, key_val)
                elif self.client.info_val['bidno'] != key_val['bidno'] or self.client.info_val['passwd'] != key_val['passwd']:
                        self.client = pp_client(self.console, self, key_val)
                if self.client != None :
                        self.client.login(key_val)

        def proc_udp_login(self, key_val):
                if self.udp == None :
                        self.udp = pp_udp(self.console, self, key_val)
                elif self.udp.info_val['udp_bidno'] != key_val['udp_bidno'] or self.udp.info_val['udp_pid'] != key_val['udp_pid']:
                        self.udp.stop()
                        self.udp = pp_udp(self.console, self, key_val)
                if self.udp != None :
                        self.udp.login(key_val)

        def proc_image_price(self, key_val):
                if self.client != None :
                        self.client.image(key_val)

        def proc_image_decode(self, key_val):
                if self.client != None :
                        self.client.price(key_val)

class Console(Console):
        def __init__(self, master=None):
                super(Console, self).__init__(master)

                self.dict_image_button = {'C' : ('连图片通道','blue'), 'S' : ('停图片通道','red')}
                self.dict_price_button = {'C' : ('连价格通道','blue'), 'S' : ('停价格通道','red')}
                self.flag_image_button = None
                self.flag_price_button = None

                self.load_database()

                self.cmd_proc = cmd_proc(self)
                self.cmd_proc.start()
                self.cmd_proc.wait_for_start()
                global proc_ssl_image, proc_ssl_price
                proc_ssl_image.reg(self)
                proc_ssl_price.reg(self)

                self.lock_login_status  = Lock()
                self.lock_bid_status    = Lock()
                self.lock_udp_status    = Lock()
                self.lock_udp_input     = Lock()
                self.lock_udp_info      = Lock()
                self.lock_price1        = Lock()
                self.lock_price2        = Lock()
                self.lock_price3        = Lock()
                self.lock_worker        = Lock()
                self.lock_image         = Lock()
                self.lock_image_button  = Lock()
                self.lock_price_button  = Lock()

        def load_database(self):
                global database
                if not hasattr(database, 'db') :
                        return

                bidno       = database.db['bidno']       if 'bidno'       in database.db else ''
                passwd      = database.db['passwd']      if 'passwd'      in database.db else ''

                udp_bidno   = database.db['udp_bidno']   if 'udp_bidno'   in database.db else ''
                udp_pid     = database.db['udp_pid']     if 'udp_pid'     in database.db else ''

                if bidno != '':
                        self.input_bidno.delete(0, 'end')
                        self.input_bidno.insert(0, bidno)

                if passwd != '':
                        self.input_passwd.delete(0, 'end')
                        self.input_passwd.insert(0, passwd)

                if udp_bidno != '':
                        self.input_udp_bidno.delete(0, 'end')
                        self.input_udp_bidno.insert(0, udp_bidno)

                if udp_pid != '':
                        self.input_udp_pid.delete(0, 'end')
                        self.input_udp_pid.insert(0, udp_pid)

        def save_database(self, key_val):
                global database
                if not hasattr(database, 'db') :
                        database.db = {}
                for key in key_val:
                        database.db[key] = key_val[key]

        #-------------------------------------
        # 按钮触发处理
        #-------------------------------------

        def proc_ssl_login(self,p1):
                key_val = {}
                key_val['cmd']    = 'ssl_login'
                key_val['bidno']  = self.input_bidno.get()
                key_val['passwd'] = self.input_passwd.get()
                key_val['group']  = self.var_use_group2.get()
                try:
                        int(key_val['bidno'])
                        int(key_val['passwd'])
                except:
                        return
                self.cmd_proc.put(key_val)

                db ={}
                db['bidno']       = key_val['bidno']
                db['passwd']      = key_val['passwd']
                self.save_database(db)

        def proc_udp_login(self,p1):
                key_val = {}
                key_val['cmd']    = 'udp_login'
                self.lock_udp_input.acquire()
                key_val['udp_bidno']  = self.input_udp_bidno.get()
                key_val['udp_pid']    = self.input_udp_pid.get()
                self.lock_udp_input.release()
                try:
                        int(key_val['udp_bidno'])
                        int(key_val['udp_pid'])
                except:
                        return
                self.cmd_proc.put(key_val)

                db ={}
                db['udp_bidno']    = key_val['udp_bidno']
                db['udp_pid']      = key_val['udp_pid']
                self.save_database(db)

        def proc_image_channel_stop(self):
                key_val = {}
                key_val['cmd']    = 'image_channel_stop'
                self.cmd_proc.put(key_val)

        def proc_price_channel_stop(self):
                key_val = {}
                key_val['cmd']    = 'price_channel_stop'
                self.cmd_proc.put(key_val)

        def proc_image_channel_connect(self):
                key_val = {}
                key_val['cmd']    = 'image_channel_connect'
                self.cmd_proc.put(key_val)

        def proc_price_channel_connect(self):
                key_val = {}
                key_val['cmd']    = 'price_channel_connect'
                self.cmd_proc.put(key_val)

        def proc_image_connect(self,p1):
                self.lock_image_button.acquire()
                if self.flag_image_button == 'C' or self.flag_image_button == None:
                        self.proc_image_channel_connect()
                        self.flag_image_button = 'S'
                        self.update_image_button('S')
                elif self.flag_image_button == 'S':
                        self.proc_image_channel_stop()
                        self.flag_image_button = 'C'
                        self.update_image_button('C')
                else:
                        logger.error('image button status error')
                self.lock_image_button.release()

        def proc_price_connect(self,p1):
                self.lock_price_button.acquire()
                if self.flag_price_button == 'C' or self.flag_price_button == None:
                        self.proc_price_channel_connect()
                        self.flag_price_button = 'S'
                        self.update_price_button('S')
                elif self.flag_price_button == 'S':
                        self.proc_price_channel_stop()
                        self.flag_price_button = 'C'
                        self.update_price_button('C')
                else:
                        logger.error('price button status error')
                self.lock_price_button.release()

        def proc_image_channel(self,p1):
                key_val = {}
                key_val['cmd']    = 'image_channel'
                key_val['size']   = self.input_image_channel.get()
                try:
                        int(key_val['size'])
                except:
                        return
                self.cmd_proc.put(key_val)

        def proc_price_channel(self,p1):
                key_val = {}
                key_val['cmd']    = 'price_channel'
                key_val['size']   = self.input_price_channel.get()
                try:
                        int(key_val['size'])
                except:
                        return
                self.cmd_proc.put(key_val)

        def proc_image_price(self,p1):
                key_val = {}
                key_val['cmd']    = 'image_price'
                key_val['price']  = self.input_image_price.get()
                try:
                        int(key_val['price'])
                except:
                        return
                key_val['group']  = self.var_use_group2.get()
                self.cmd_proc.put(key_val)

        def proc_image_decode(self,p1):
                key_val = {}
                key_val['cmd']    = 'image_decode'
                key_val['image']  = self.input_image_decode.get()
                try:
                        int(key_val['image'])
                except:
                        return
                self.cmd_proc.put(key_val)

        #-------------------------------------
        # 回调接口
        #-------------------------------------

        def update_image_button(self, info):
                try:
                        text  = self.dict_image_button[info][0]
                        color = self.dict_image_button[info][1]
                except:
                        print_exc()
                        return
                self.button_image_connect['text']               = text
                self.button_image_connect['foreground']         = color
                self.button_image_connect['activeforeground']   = color
                self.button_image_connect.update_idletasks()

        def update_price_button(self, info):
                try:
                        text  = self.dict_price_button[info][0]
                        color = self.dict_price_button[info][1]
                except:
                        print_exc()
                        return
                self.button_price_connect['text']               = text
                self.button_price_connect['foreground']         = color
                self.button_price_connect['activeforeground']   = color
                self.button_price_connect.update_idletasks()

        def update_login_status(self, info):
                self.lock_login_status.acquire()
                self.output_login_status['text']    = info
                self.output_login_status.update_idletasks()
                self.lock_login_status.release()

        def update_udp_status(self, info):
                self.lock_udp_status.acquire()
                self.output_udp_status['text']      = info
                self.output_udp_status.update_idletasks()
                self.lock_udp_status.release()

        def update_bid_status(self, info):
                self.lock_bid_status.acquire()
                self.output_bid_status['text']      = info
                self.output_bid_status.update_idletasks()
                self.lock_bid_status.release()

        def update_udp_input(self, bidno, pid):
                self.lock_udp_input.acquire()
                self.input_udp_bidno.delete(0, 'end')
                self.input_udp_pid.delete(0, 'end')
                self.input_udp_bidno.insert(0, bidno)
                self.input_udp_pid.insert(0, pid)
                self.input_udp_pid.update_idletasks()
                #self.input_udp_bidno.update_idletasks()
                self.lock_udp_input.release()

        def update_udp_info(self, ctime, stime, price):
                self.lock_udp_info.acquire()
                self.output_current_price['text']   = price
                self.output_system_time['text']     = stime
                self.output_change_time['text']     = ctime
                self.output_current_price.update_idletasks()
                #self.output_system_time.update_idletasks()
                #self.output_change_time.update_idletasks()
                self.lock_udp_info.release()

        def update_image_channel(self, current, goal, onway):
                self.output_image_current_channel['text'] = current
                self.output_image_goal_channel['text']    = goal
                self.output_image_onway_channel['text']   = onway
                self.output_image_current_channel.update_idletasks()
                #self.output_image_goal_channel.update_idletasks()

        def update_price_channel(self, current, goal, onway):
                self.output_price_current_channel['text'] = current
                self.output_price_goal_channel['text']    = goal
                self.output_price_onway_channel['text']   = onway
                self.output_price_current_channel.update_idletasks()
                #self.output_price_goal_channel.update_idletasks()

        def update_first_price(self, info):
                self.lock_price1.acquire()
                self.output_first_price['text']     = info
                self.output_first_price.update_idletasks()
                self.lock_price1.release()

        def update_second_price(self, info):
                self.lock_price2.acquire()
                self.output_second_price['text']    = info
                self.output_second_price.update_idletasks()
                self.lock_price2.release()

        def update_third_price(self, info):
                self.lock_price3.acquire()
                self.output_third_price['text']     = info
                self.output_third_price.update_idletasks()
                self.lock_price3.release()

        def update_price_worker(self, info):
                self.lock_worker.acquire()
                self.output_price_onway_work['text']= info
                self.output_price_onway_work.update_idletasks()
                self.lock_worker.release()

        def update_image_decode(self, image, price):
                try:
                        image = b64decode(image)
                        photo = ImageTk.PhotoImage(Image.open(BytesIO(image)))
                except:
                        global err_jpg
                        self.lock_image.acquire()
                        self.output_image.image     = err_jpg
                        self.output_image['image']  = err_jpg
                        self.output_image.update_idletasks()
                        self.lock_image.release()
                        self.save_jpg(image)
                        logger.error('图片错误，重新请求')
                else:
                        self.lock_image.acquire()
                        self.output_image.image         = photo
                        self.output_image['image']      = photo
                        self.output_last_price['text']  = price
                        self.output_image.update_idletasks()
                        self.lock_image.release()
                        #self.output_last_price.update_idletasks()

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

