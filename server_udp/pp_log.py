#!/usr/bin/env python3

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

class console_logger():
        def debug(self, log):
                print('debug:    ',log)

        def info(self, log):
                print('info:     ',log)

        def warning(self, log):
                print('warning:  ',log)

        def error(self, log):
                print('error:    ',log)

        def critical(self, log):
                print('critical: ',log)

logger  = console_logger()
printer = console_logger()

