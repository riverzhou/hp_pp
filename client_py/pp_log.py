#!/usr/bin/env python3



import logging


def make_log(name = None, log = None,  level = 'debug' , console = True, fmt = True):
        LEVELS = {
                'debug'   : logging.DEBUG,
                'info'    : logging.INFO,
                'warning' : logging.WARNING,
                'error'   : logging.ERROR,
                'critical': logging.CRITICAL}

        if not level in LEVELS :
                level = 'debug' 
        else:
                level = LEVELS[level]

        # 创建一个logger
        if log != None :
                logger = logging.getLogger(log)
        else :
                logger = logging.getLogger()

        logger.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        if fmt != False :
                #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                formatter = logging.Formatter('%(asctime)s - %(levelname)-8s ->|%(message)s')
        else :
                formatter = logging.Formatter()

        # 创建一个handler，用于写入日志文件，再添加到logger
        if name != None :
                fh = logging.FileHandler(name)
                fh.setLevel(level)
                fh.setFormatter(formatter)
                logger.addHandler(fh)

        # 再创建一个handler，用于输出到控制台，添加到logger
        if console != False :
                ch = logging.StreamHandler()
                ch.setLevel(level)
                ch.setFormatter(formatter)
                logger.addHandler(ch)

        # 记录一条日志
        #logger.info('foorbar')

        return logger


logger = make_log(log = 'logger')
printer = make_log(log = 'printer', fmt = False)

ct_printer = make_log(log = 'ct_printer', level = 'error', fmt = False)
pp_printer = make_log(log = 'pp_printer', level = 'info',  fmt = False)

