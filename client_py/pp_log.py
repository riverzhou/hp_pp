#!/usr/bin/env python3



import logging


def make_log(file_name, level = 'debug' , ifConsole = False):
        LEVELS = {
                'debug'   : logging.DEBUG,
                'info'    : logging.INFO,
                'warning' : logging.WARNING,
                'error'   : logging.ERROR,
                'critical': logging.CRITICAL}

        if not level in LEVELS :
                level = False
        else:
                level = LEVELS[level]

        # 创建一个logger
        #logger = logging.getLogger('pp_log')
        logger = logging.getLogger()
        if not level == False :
                logger.setLevel(level)

        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(file_name)
        if not level == False :
                fh.setLevel(level)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        if not level == False :
                ch.setLevel(level)

        # 定义handler的输出格式
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(levelname)-8s ->|%(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        logger.addHandler(fh)
        if ifConsole == True :
                logger.addHandler(ch)

        # 记录一条日志
        #logger.info('foorbar')

        return logger
