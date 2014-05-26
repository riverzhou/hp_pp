#!/usr/bin/env python3

class foobar_printer():
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

class foobar_logger(foobar_printer):
        pass

logger  = foobar_logger()
printer = foobar_printer()

