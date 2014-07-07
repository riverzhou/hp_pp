#!/usr/bin/env python3

#=========================================================================================

class foobar_logger():
        def debug(self,log):    pass

        def info(self,log):     pass

        def warning(self,log):  pass

        def error(self,log):    pass

        def critical(self,log): pass

        def wait_for_flush(self): pass

#-----------------------------------------------------------------------------------------

printer = foobar_logger()
logger  = foobar_logger()

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
        printer.wait_for_flush()

