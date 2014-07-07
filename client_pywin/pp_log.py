#!/usr/bin/env python3

import  logging
import  platform
from    threading       import Thread, Event, Lock, Semaphore
from    queue           import Queue, LifoQueue
from    datetime        import datetime
from    redis           import StrictRedis
from    traceback       import print_exc
from    pickle          import dumps, loads

from    pp_config       import pp_config

#=========================================================================================

class foobar_logger():
        def debug(self,log):    pass

        def info(self,log):     pass

        def warning(self,log):  pass

        def error(self,log):    pass

        def critical(self,log): pass

        def wait_for_flush(self): pass

#-----------------------------------------------------------------------------------------

class pp_thread(Thread):
        def __init__(self, info = ''):
                Thread.__init__(self)
                self.flag_stop     = False
                self.event_stop    = Event()
                self.event_started = Event()
                self.thread_info   = info
                self.setDaemon(True)

        def wait_for_start(self):
                self.event_started.wait()

        def stop(self):
                self.flag_stop = True
                self.event_stop.set()

        def run(self):
                print('Thread %s : Id %s : %s : started' % (self.__class__.__name__, self.ident, self.thread_info))
                self.event_started.set()
                try:
                        self.main()
                except KeyboardInterrupt:
                        pass
                print('Thread %s : Id %s : %s : stoped' % (self.__class__.__name__, self.ident, self.thread_info))

        def main(self): pass

class pp_sender(pp_thread):
        def __init__(self, info = '', lifo = False):
                pp_thread.__init__(self, info)
                self.queue = Queue() if not lifo else LifoQueue()

        def put(self, buff):
                self.queue.put(buff)

        def stop(self):
                pp_thread.stop(self)
                self.put(None)

        def get(self):
                try:
                        return self.queue.get()
                except KeyboardInterrupt:
                        raise KeyboardInterrupt

        def main(self):
                while True:
                        buff = self.get()
                        if self.flag_stop  == True or not buff  : break
                        if self.proc(buff) == True              : self.queue.task_done()
                        if self.flag_stop  == True              : break

        def proc(self, buff): pass

class redis_sender(pp_sender):
        def __init__(self, redis, info):
                pp_sender.__init__(self, info)
                self.redis = redis

        def send(self, buff):
                self.put(buff)

        def proc(self, buff):
                try:
                        self.redis.rpush(buff[0], buff[1])
                        return True
                except KeyboardInterrupt:
                        raise KeyboardInterrupt
                except:
                        print_exc()
                        return False

class redis_logger():
        dict_log_level= {
                        'all'      : 0,
                        'debug'    : 10,
                        'info'     : 20,
                        'warning'  : 30,
                        'error'    : 40,
                        'critical' : 50,
                        'null'     : 60,
                        }
        def __init__(self, level = 'debug'):
                self.redis = self.connect_redis()
                if self.redis == None : return None

                level = level if level in self.dict_log_level else 'debug'

                self.log_level = self.dict_log_level[level]

                self.redis_sender = redis_sender(self.redis, 'redis_sender')
                self.redis_sender.start()
                self.redis_sender.wait_for_start()

        def debug(self, log, bin=False):
                if self.log_level > self.dict_log_level['debug']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.send(('debug', dumps((time, log),0)))
                else:
                        self.redis_sender.send(('debug', (time, log)))

        def info(self, log, bin=False):
                if self.log_level > self.dict_log_level['info']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.send(('info', dumps((time, log),0)))
                else:
                        self.redis_sender.send(('info', (time, log)))

        def warning(self, log, bin=False):
                if self.log_level > self.dict_log_level['warning']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.send(('warning', dumps((time, log),0)))
                else:
                        self.redis_sender.send(('warning', (time, log)))

        def error(self, log, bin=False):
                if self.log_level > self.dict_log_level['error']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.send(('error', dumps((time, log),0)))
                else:
                        self.redis_sender.send(('error', (time, log)))

        def critical(self, log, bin=False):
                if self.log_level > self.dict_log_level['critical']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                if bin == True:
                        self.redis_sender.send(('critical', dumps((time, log),0)))
                else:
                        self.redis_sender.send(('critical', (time, log)))

        def wait_for_flush(self):
                self.redis_sender.queue.join()

        def connect_redis(self):
                global pp_config
                redis_passwd  = pp_config['redis_pass']
                redis_port    = pp_config['redis_port']
                redis_ip      = pp_config['redis_ip']
                redis_db      = pp_config['redis_db']
                try:
                        return StrictRedis(host = redis_ip, port = redis_port, password = redis_passwd, db = redis_db)
                except:
                        print_exc()
                        return None

#-----------------------------------------------------------------------------------------

if platform.system() == 'Windows' :
        import ctypes

class windows_logger():
        '''
            0 = 黑色       8 = 灰色
            1 = 蓝色       9 = 淡蓝色
            2 = 绿色       A = 淡绿色
            3 = 浅绿色     B = 淡浅绿色
            4 = 红色       C = 淡红色
            5 = 紫色       D = 淡紫色
            6 = 黄色       E = 淡黄色
            7 = 白色       F = 亮白色
        '''
        BLACK, BLUE, GREEN, BLACKGREEN, RED, PURPLE, YELLOW, WHITE, GRAY, LIGHTBLUE, LIGHTGREEN, LIGHTBLACKGREEN, LIGHTRED, LIGHTPURPLE, LIGHTYELLOW, HIGHWHITE = range(16)
        COLORS = {
                'DEBUG'   : GREEN,
                'INFO'    : GRAY,
                'WARNING' : BLACKGREEN,
                'ERROR'   : LIGHTRED,
                'CRITICAL': LIGHTYELLOW,
                }
        STD_HANDLE = -11

        def __init__(self, name = None, log = None,  level = 'debug' , console = True, fmt = True, color = True):
                LEVELS = {
                        'debug'   : logging.DEBUG,
                        'info'    : logging.INFO,
                        'warning' : logging.WARNING,
                        'error'   : logging.ERROR,
                        'critical': logging.CRITICAL
                        }
                if console == True and color == True :
                        self.std_handle = ctypes.windll.kernel32.GetStdHandle(self.STD_HANDLE)
                        self.flag_color = True
                else:
                        self.flag_color = False
                level = LEVELS[level] if level in LEVELS else 'debug'
                # 创建一个logger
                logger = logging.getLogger(log) if log != None else logging.getLogger()
                logger.setLevel(logging.DEBUG)
                # 定义handler的输出格式
                NORMAL_FORMAT     = '%(asctime)s - %(levelname)-8s ->|%(message)s'
                normal_formatter  = logging.Formatter(NORMAL_FORMAT)
                none_formatter    = logging.Formatter()
                screen_formatter  = normal_formatter  if fmt == True   else none_formatter
                file_formatter    = normal_formatter  if fmt == True   else none_formatter
                # 创建一个handler，用于写入日志文件，再添加到logger
                if name != None :
                        fh = logging.FileHandler(name)
                        fh.setLevel(level)
                        fh.setFormatter(file_formatter)
                        logger.addHandler(fh)
                # 再创建一个handler，用于输出到控制台，添加到logger
                if console != False :
                        ch = logging.StreamHandler()
                        ch.setLevel(level)
                        ch.setFormatter(screen_formatter)
                        logger.addHandler(ch)
                self.logger = logger

        def set_color(self,color):
                ctypes.windll.kernel32.SetConsoleTextAttribute(self.std_handle, color)

        def debug(self,message):
                if self.flag_color : self.set_color(self.COLORS['DEBUG'])
                self.logger.debug(message)
                if self.flag_color : self.set_color(self.WHITE)

        def info(self,message):
                if self.flag_color : self.set_color(self.COLORS['INFO'])
                self.logger.info(message)
                if self.flag_color : self.set_color(self.WHITE)

        def warning(self,message):
                if self.flag_color : self.set_color(self.COLORS['WARNING'])
                self.logger.warn(message)
                if self.flag_color : self.set_color(self.WHITE)

        def error(self,message):
                if self.flag_color : self.set_color(self.COLORS['ERROR'])
                self.logger.error(message)
                if self.flag_color : self.set_color(self.WHITE)

        def critical(self,message):
                if self.flag_color : self.set_color(self.COLORS['CRITICAL'])
                self.logger.critical(message)
                if self.flag_color : self.set_color(self.WHITE)

#-----------------------------------------------------------------------------------------

class ColoredFormatter(logging.Formatter):
        BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(30, 38)
        COLORS = {
                'DEBUG'   : GREEN,
                'INFO'    : WHITE,
                'WARNING' : BLUE,
                'ERROR'   : RED,
                'CRITICAL': YELLOW,
                }
        RESET_SEQ = "\033[0m"
        COLOR_SEQ = "\033[1;%dm"
        BOLD_SEQ  = "\033[1m"

        def format(self, record):
                levelname = record.levelname
                if levelname in self.COLORS :
                        record.levelname = self.COLOR_SEQ % self.COLORS[levelname] + levelname + self.RESET_SEQ
                return logging.Formatter.format(self, record)

class posix_logger():
        def __init__(self, name = None, log = None,  level = 'debug' , console = True, fmt = True, color = True):
                LEVELS = {
                        'debug'   : logging.DEBUG,
                        'info'    : logging.INFO,
                        'warning' : logging.WARNING,
                        'error'   : logging.ERROR,
                        'critical': logging.CRITICAL
                        }
                level = LEVELS[level] if level in LEVELS else 'debug'
                # 创建一个logger
                logger = logging.getLogger(log) if log != None else logging.getLogger()
                logger.setLevel(logging.DEBUG)
                # 定义handler的输出格式
                COLOR_FORMAT      = '%(asctime)s - %(levelname)-19s ->|%(message)s'
                NORMAL_FORMAT     = '%(asctime)s - %(levelname)-8s ->|%(message)s'
                color_formatter   = ColoredFormatter(COLOR_FORMAT)
                normal_formatter  = logging.Formatter(NORMAL_FORMAT)
                none_formatter    = logging.Formatter()
                color_formatter   = color_formatter   if color == True else normal_formatter 
                screen_formatter  = color_formatter   if fmt == True   else none_formatter
                file_formatter    = normal_formatter  if fmt == True   else none_formatter
                # 创建一个handler，用于写入日志文件，再添加到logger
                if name != None :
                        fh = logging.FileHandler(name)
                        fh.setLevel(level)
                        fh.setFormatter(file_formatter)
                        logger.addHandler(fh)
                # 再创建一个handler，用于输出到控制台，添加到logger
                if console != False :
                        ch = logging.StreamHandler()
                        ch.setLevel(level)
                        ch.setFormatter(screen_formatter)
                        logger.addHandler(ch)
                self.logger = logger

        def debug(self,message):
                self.logger.debug(message)

        def info(self,message):
                self.logger.info(message)

        def warning(self,message):
                self.logger.warn(message)

        def error(self,message):
                self.logger.error(message)

        def critical(self,message):
                self.logger.critical(message)

#-----------------------------------------------------------------------------------------

def make_log(name = None, log = None,  level = 'debug' , console = True, fmt = True, color = True):
        if platform.system() == 'Windows' :
                return windows_logger(name, log,  level, console, fmt, color)
        else :
                return posix_logger(name, log,  level, console, fmt, color)

#=========================================================================================

logger     = make_log(name = None,          log = 'logger',     level = 'debug', console = True, fmt = True,  color = True)

#logger    = make_log(name = 'log.log',     log = 'logger',     level = 'debug', console = True, fmt = True,  color = True)
#printer   = make_log(name = 'pri.log',     log = 'printer',    level = 'debug', console = True, fmt = False, color = False)

#-----------------------------------------------------------------------------------------

printer    = redis_logger()
if printer.redis == None : printer = foobar_logger()

'''
logger     = foobar_logger()
printer    = foobar_logger()
'''

#================================ for test ===============================================

if __name__ == "__main__":
        logger.debug('test logger debug')
        logger.info('test logger info')
        logger.warning('test logger warning')
        logger.error('test logger error')
        logger.critical('test logger critical')
        #printer.debug('test printer debug')
        #printer.info('test printer info')
        #printer.warning('test printer warning')
        #printer.error('test printer error')
        #printer.critical('test printer critical')
        #printer.wait_for_flush()

