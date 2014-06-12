#!/usr/bin/env python3

import logging
import platform
from datetime  import datetime
from pp_redis  import red

#=========================================================================================

class foobar_logger():
        def debug(self,log):    pass

        def info(self,log):     pass

        def warning(self,log):  pass

        def error(self,log):    pass

        def critical(self,log): pass

#-----------------------------------------------------------------------------------------

class redis_logger():
        def __init__(self, redis):
                self.redis = redis

        def debug(self, log):
                time = datetime.strftime(datetime.now(), '%y-%m-%d %H:%M:%S.%f')
                self.redis.rpush('debug',(time, log))

        def info(self, log):
                time = datetime.strftime(datetime.now(), '%y-%m-%d %H:%M:%S.%f')
                self.redis.rpush('info',(time, log))

        def warning(self, log):
                time = datetime.strftime(datetime.now(), '%y-%m-%d %H:%M:%S.%f')
                self.redis.rpush('warning',(time, log))

        def error(self, log):
                time = datetime.strftime(datetime.now(), '%y-%m-%d %H:%M:%S.%f')
                self.redis.rpush('error',(time, log))

        def critical(self, log):
                time = datetime.strftime(datetime.now(), '%y-%m-%d %H:%M:%S.%f')
                self.redis.rpush('critical',(time, log))

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
                'ERROR'   : RED,
                'CRITICAL': YELLOW,
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

logger    = make_log(name = 'log.log',     log = 'logger',     level = 'debug', console = True, fmt = True,  color = True)
printer   = make_log(name = 'pri.log',     log = 'printer',    level = 'debug', console = True, fmt = False, color = False)

#-----------------------------------------------------------------------------------------

#printer    = redis_logger(red)

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
        printer.debug('test printer debug')
        printer.info('test printer info')
        printer.warning('test printer warning')
        printer.error('test printer error')
        printer.critical('test printer critical')


