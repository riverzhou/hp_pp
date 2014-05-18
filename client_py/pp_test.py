#!/usr/bin/env python3

from pp_log import make_log


logger = None

def pp_test():
        global logger
        logger = make_log('pp_test.log', 'debug', True)
        logger.info('test info')
        logger.debug('test debug')
        logger.warning('test warning')
        logger.error('test error')

if __name__ == "__main__":
        pp_test()




