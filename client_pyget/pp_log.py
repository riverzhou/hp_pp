#!/usr/bin/env python3

import logging
import platform

#=========================================================================================

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

class foobar_logger():
        def debug(self, log):
                pass
        def info(self, log):
                pass
        def warning(self, log):
                pass
        def error(self, log):
                pass
        def critical(self, log):
                pass

#-----------------------------------------------------------------------------------------

def make_log(name = None, log = None,  level = 'debug' , console = True, fmt = True, color = True):

        color = False if platform.system() == 'Windows' else color

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

        return logger

#=========================================================================================
'''
logger     = make_log(name = 'log.log',     log = 'logger',     level = 'debug', console = True, fmt = True,  color = True)
printer    = make_log(name = 'pri.log',     log = 'printer',    level = 'debug', console = True, fmt = False, color = False)
'''
#=========================================================================================

logger     = foobar_logger()
printer    = foobar_logger()

#================================ for test ===============================================

if __name__ == "__main__":
        logger.debug('test logger debug')
        logger.info('test logger info')
        logger.warning('test logger warning')
        logger.error('test logger error')
        logger.critical('test logger critical')

