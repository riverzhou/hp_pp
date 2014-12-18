#!/usr/bin/env python3

from time                   import sleep
from traceback              import print_exc, format_exc
from redis                  import StrictRedis
from threading              import Event, Lock, Thread

from fd_config              import redis_ip, redis_port, redis_passwd, redis_dbid
from fd_log                 import logger

#======================================================================

class redis_db(Thread):

        def __init__(self, redis_ip, redis_port, redis_passwd, redis_dbid):
                super().__init__()
                self.setDaemon(True)

                self.redis              = None

                self.event_conn_ok      = Event()
                self.flag_do_reconn     = True
                self.lock_do_reconn     = Lock()

                self.event_conn_chk     = Event()
                self.event_conn_chk.set()

                self.redis_ip           = redis_ip
                self.redis_port         = redis_port
                self.redis_passwd       = redis_passwd
                self.redis_dbid         = redis_dbid

        def run(self):
                while True:
                        self.event_conn_chk.wait()
                        self.reconnect_redis()
                        sleep(0.1)

        def reconnect_redis(self):
                self.lock_do_reconn.acquire()
                if self.flag_do_reconn == True:
                        while True:
                                if self.redis != None:
                                        del(self.redis)
                                self.redis = self.connect_redis()
                                sleep(1)
                                try:
                                        if self.redis.echo('echo') == b'echo':
                                                break
                                        else:
                                                continue
                                except  KeyboardInterrupt:
                                        break
                                except:
                                        continue
                        self.flag_do_reconn = False
                        self.event_conn_ok.set()
                        self.event_conn_chk.clear()
                self.lock_do_reconn.release()

        def check_connect_ok(self):
                try:
                        return self.event_conn_ok.wait()
                except  KeyboardInterrupt:
                        return None
                except:
                        return False

        def set_connect_error(self):
                if self.lock_do_reconn.acquire(blocking = False) == False:
                        return False
                if self.flag_do_reconn != True:
                        self.flag_do_reconn = True
                        self.event_conn_ok.clear()
                        self.event_conn_chk.set()
                self.lock_do_reconn.release()
                return  True

        def connect_redis(self):
                try:
                        return StrictRedis(host = self.redis_ip, port = self.redis_port, password = self.redis_passwd, db = self.redis_dbid, socket_keepalive = True)
                except  KeyboardInterrupt:
                        return None
                except:
                        print_exc()
                        return None

        def safe_proc(self, proc):
                def _safe_proc(*args, **kwargs):
                        ret = None
                        while True:
                                if self.check_connect_ok() != True:
                                        sleep(0.1)
                                        continue
                                try:
                                        ret = proc(*args, **kwargs)
                                except  KeyboardInterrupt:
                                        return None
                                except:
                                        self.set_connect_error()
                                        logger.critical(format_exc())
                                        sleep(0.1)
                                        continue
                                break
                        return ret
                return _safe_proc

        def save(self):
                if self.redis == None:
                        return False
                try:
                        self.redis.save()
                except  KeyboardInterrupt:
                        return False
                except:
                        logger.critical(format_exc())
                        return False
                return True

#===================================================================

pp_redis = redis_db(redis_ip, redis_port, redis_passwd, redis_dbid)

def pp_redis_init():
        global pp_redis
        pp_redis.start()
        if pp_redis.check_connect_ok() == True:
                pp_redis_connect_print()
                return True
        else:
                return False

def pp_redis_connect_print():
        global pp_redis
        logger.warning(pp_redis.redis)

if __name__ == "__main__":
        pp_redis_init()
        logger.wait_for_flush()

