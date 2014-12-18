#!/usr/bin/env python3

import  logging
from    threading           import Thread, Event, Lock
from    queue               import Queue
from    datetime            import datetime
from    traceback           import print_exc
from    pickle              import dumps, loads

from    fd_config           import local_logfile

#=================================================================================

class file_writer(Thread):
        def __init__(self, info):
                global local_logfile
                super().__init__()
                self.setDaemon(True)
                self.event_started  = Event()
                self.thread_info    = info
                self.queue          = Queue()
                self.logfile        = open(local_logfile, 'a')

        def wait_for_start(self, timeout = None):
                if timeout == None:
                        self.event_started.wait()
                else:
                        try:
                                int(timeout)
                        except  KeyboardInterrupt:
                                pass
                        except:
                                print_exc()
                                self.event_started.wait(self.default_start_timeout)
                        else:
                                self.event_started.wait(timeout)

        def run(self):
                self.event_started.set()
                try:
                        self.main()
                except  KeyboardInterrupt:
                        pass

        def main(self):
                while True:
                        buff = self.get()
                        if buff == None:
                                sleep(0)
                                continue
                        if self.send(buff) == True : 
                                self.queue.task_done()

        def put(self, buff):
                self.queue.put(buff)

        def get(self):
                try:
                        return self.queue.get()
                except  KeyboardInterrupt:
                        return None
                except:
                        print_exc()
                        return None

        def send(self, buff):
                self.logfile.write(buff[1][0] + '\t' + '['+  buff[0] + ']' + '\t' + buff[1][1] + '\n')
                self.logfile.flush()
                return True

        def wait_for_flush(self):
                return self.queue.join()

#--------------------------------------------------------------------------------

class file_logger():
        dict_log_level= {
                        'all'      : 0,
                        'debug'    : 10,
                        'info'     : 20,
                        'warning'  : 30,
                        'error'    : 40,
                        'critical' : 50,
                        'data'     : 60,
                        'time'     : 70,
                        'record'   : 80,
                        'null'     : 90,
                        }

        def __init__(self, level = 'debug'):
                level = level if level in self.dict_log_level else 'debug'
                self.log_level = self.dict_log_level[level]

                self.file_writer = file_writer('file_writer')
                self.file_writer.start()
                self.file_writer.wait_for_start()

        def debug(self, log, bin=False):
                if self.log_level > self.dict_log_level['debug']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                self.file_writer.put(('log_debug', (time, str(log))))

        def info(self, log, bin=False):
                if self.log_level > self.dict_log_level['info']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                self.file_writer.put(('log_info', (time, str(log))))

        def warning(self, log, bin=False):
                if self.log_level > self.dict_log_level['warning']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                self.file_writer.put(('log_warning', (time, str(log))))

        def error(self, log, bin=False):
                if self.log_level > self.dict_log_level['error']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                self.file_writer.put(('log_error', (time, str(log))))

        def critical(self, log, bin=False):
                if self.log_level > self.dict_log_level['critical']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                self.file_writer.put(('log_critical', (time, str(log))))

        def data(self, log, bin=False):
                if self.log_level > self.dict_log_level['data']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                self.file_writer.put(('log_data', (time, str(log))))

        def time(self, log, bin=False):
                if self.log_level > self.dict_log_level['time']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                self.file_writer.put(('log_time', (time, str(log))))

        def record(self, log, bin=False):
                if self.log_level > self.dict_log_level['record']: return
                time = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')
                self.file_writer.put(('log_record', (time, str(log))))

        def wait_for_flush(self):
                self.file_writer.wait_for_flush()

#-----------------------------------------------------------------------------------------

logger  = file_logger()

#================================ for test ===============================================

if __name__ == "__main__":
        from pp_baseredis  import pp_redis_init
        pp_redis_init()
        logger.debug('test logger debug')
        logger.info('test logger info')
        logger.warning('test logger warning')
        logger.error('test logger error')
        logger.critical('test logger critical')
        logger.data('test logger data')
        logger.time('test logger time')
        logger.record('record logger time')
        logger.wait_for_flush()

