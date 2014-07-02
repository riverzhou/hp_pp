#!/usr/bin/env python3

from    threading       import Thread, Event, Lock, Semaphore
from    queue           import Queue, LifoQueue
from    redis           import StrictRedis
from    traceback       import print_exc
from    pickle          import dumps, loads
from    time            import sleep, time, localtime, mktime, strptime, strftime

from    pp_baseclass    import pp_thread, pp_sender
from    pp_config       import pp_config

#=========================================================================================

class redis_pickle(pp_sender):
        key_a = 'painter_a'
        key_b = 'painter_b'

        def connect_redis(self):
                global pp_config
                redis_passwd  = pp_config['redis_pass']
                redis_port    = pp_config['redis_port']
                redis_ip      = pp_config['redis_ip']
                redis_db      = pp_config['redis_db']
                try:
                        return StrictRedis(host = redis_ip, port = redis_port, password = redis_passwd, db = redis_db)
                except:
                        print_exc()
                        return None

        def __init__(self, info=''):
                pp_sender.__init__(self, info)
                self.redis    = self.connect_redis()
                if self.redis == None : return None

        def proc(self, buff):
                code, info = buff
                if code == 'A' : return self.redis.put(self.key_a, info)
                if code == 'B' : return self.redis.put(self.key_b, info)
                return None

        def load(self, code):
                if code == 'A' :
                        try:
                                return self.redis.get(self.key_a)
                        except:
                                print_exc()
                                return None
                if code == 'B' :
                        try:
                                return self.redis.get(self.key_b)
                        except:
                                print_exc()
                                return None
                return None


class redis_reader(pp_thread):
        key_name = pp_config['redis_key']

        def __init__(self, mode, output=None, info=''):
                pp_thread.__init__(self, info)
                self.mode     = mode
                self.output   = output
                self.redis    = self.connect_redis()
                if self.redis == None : return None

        def connect_redis(self):
                global pp_config
                redis_passwd  = pp_config['redis_pass']
                redis_port    = pp_config['redis_port']
                redis_ip      = pp_config['redis_ip']
                redis_db      = pp_config['redis_db']
                try:
                        return StrictRedis(host = redis_ip, port = redis_port, password = redis_passwd, db = redis_db)
                except:
                        print_exc()
                        return None

        def get_info(self):
                try:
                        return self.redis.blpop(self.key_name)
                except  KeyboardInterrupt:
                        raise KeyboardInterrupt
                except:
                        print_exc()
                        return None

        def main(self):
                if self.mode != 'A' and self.mode != 'B' : return
                while True:
                        redis_info = self.get_info()
                        if redis_info == None : break
                        time, key_val = loads(redis_info[1])
                        #time = time.split(' ')[1].split('.')[0]
                        #print(key_val)
                        if self.mode == 'A' and key_val['code'] == 'B' :
                                if self.output != None : self.output.set_flag_end()
                                break
                        if self.output != None : self.output.put(key_val)

class redis_parser(pp_thread):
        def __init__(self, mode, output=None, info=''):
                pp_thread.__init__(self, info)
                self.mode           = mode
                self.output         = output

                self.origin_data_a  = []
                self.origin_data_b  = []
                self.lock_data_a    = Lock()
                self.lock_data_b    = Lock()

                self.result_data_a  = ([],[],[])
                self.result_data_b  = ([],[],[])
                self.result_count_a = 0
                self.result_count_b = 0

                #-----------------------------
                self.pickle     =  redis_pickle('redis_pickle')
                if self.pickle  == None : return None
                self.pickle.start()
                self.pickle.wait_for_start()

                pickle_a = self.pickle.load('A')
                pickle_b = self.pickle.load('B')

                if pickle_a != None :
                        self.origin_data_a = loads(pickle_a)

                if pickle_b != None :
                        self.origin_data_b = loads(pickle_b)

                #-----------------------------
                self.flag_end   =  False
                self.reader     =  redis_reader(self.mode, self, 'redis_reader')
                if self.reader  == None : return None
                self.reader.start()
                self.reader.wait_for_start()

        def set_flag_end(self):
                self.flag_end = True

        def put(self, info):
                try:
                        code = info['code']
                except:
                        print('code error')
                        return
                if code == 'A' :
                        self.lock_data_a.acquire()
                        self.origin_data_a.append(info)
                        self.pickle.put('A', dumps(self.origin_data_a))
                        self.lock_data_a.release()
                elif code == 'B' :
                        self.lock_data_b.acquire()
                        self.origin_data_b.append(info)
                        self.pickle.put('B', dumps(self.origin_data_b))
                        self.lock_data_b.release()
                else:
                        print('unknow code')

        def sub_time(self, time2, time1):
                return int(mktime(strptime('1970-01-01 '+time2, "%Y-%m-%d %H:%M:%S"))) - int(mktime(strptime('1970-01-01 '+time1, "%Y-%m-%d %H:%M:%S")))
        
        def add_time(self, time):
                return strftime("%H:%M:%S", localtime(int(mktime(strptime('1970-01-01 '+time, "%Y-%m-%d %H:%M:%S"))) + 1))

        def clear_data_a(self):
                self.result_data_a  = ([],[],[])
                self.result_count_a = 0

        def clear_data_b(self):
                self.result_data_b  = ([],[],[])
                self.result_count_b = 0

        def parse_data_a(self):
                last_time   = None
                last_number = None
                data = []
                self.lock_data_a.acquire()
                for info in self.origin_data_a :
                        data.append(info)
                self.lock_data_a.release()
                for parse in data:
                        time   = parse['systime']
                        number = int(parse['number'])
                        if last_time == None :
                                last_time   = time
                                last_number = number
                                self.write_result_a((time, number))
                                continue
                        delta_time = self.sub_time(time, last_time)
                        if delta_time <= 0 :
                                continue
                        if delta_time >  1 :
                                lost_time = last_time
                                for i in range(delta_time - 1) :
                                        lost_time = self.add_time(lost_time)
                                        self.write_result_a((lost_time, last_number))
                        last_time   = time
                        last_number = number
                        self.write_result_a((time, number))
        
        def parse_data_b(self):
                last_time   = None
                last_price  = None
                data = []
                self.lock_data_b.acquire()
                for info in self.origin_data_b :
                        data.append(info)
                self.lock_data_b.release()
                for parse in data:
                        time   = parse['systime']
                        price  = int(parse['price'])
                        if last_time == None :
                                last_time   = time
                                last_price  = price
                                self.write_result_b((time, price))
                                continue
                        delta_time = self.sub_time(time, last_time)
                        if delta_time <= 0 :
                                continue
                        if delta_time >  1 :
                                lost_time = last_time
                                for i in range(delta_time - 1) :
                                        lost_time = self.add_time(lost_time)
                                        self.write_result_b((lost_time, last_price))
                        last_time   = time
                        last_price  = price
                        self.write_result_b((time, price))

        def write_result_a(self, result):
                self.result_data_a[2].append(result[0])
                self.result_data_a[1].append(result[1])
                self.result_data_a[0].append(self.result_count_a)
                self.result_count_a += 1

        def write_result_b(self, result):
                if len(self.result_data_b[2]) < 60:
                        self.result_data_b[2].append(result[0])
                else:
                        del(self.result_data_b[2][0])
                        self.result_data_b[2].append(result[0])

                if len(self.result_data_b[1]) < 60:
                        self.result_data_b[1].append(result[1])
                else:
                        del(self.result_data_b[1][0])
                        self.result_data_b[1].append(result[1])

                if self.result_count_b < 60:
                        self.result_data_b[0].append(self.result_count_b)
                        self.result_count_b += 1

        def send_result_a(self):
                if self.output != None:
                        #self.output.put_a(self.result_data_a)
                        self.output.put(self.result_data_a)
                else:
                        print(self.result_data_a)

        def send_result_b(self):
                if self.output != None:
                        #self.output.put_b(self.result_data_b)
                        self.output.put(self.result_data_b)
                else:
                        print(self.result_data_b)

        def proc_a(self):
                self.clear_data_a()
                self.parse_data_a()
                self.send_result_a()

        def proc_b(self):
                self.clear_data_b()
                self.parse_data_b()
                self.send_result_b()

        def main(self):
                if self.mode == 'A' :
                        while True:
                                self.proc_a()
                                if self.flag_end : break
                                sleep(1-(time() % 1))
                elif self.mode == 'B' :
                        while True:
                                self.proc_b()
                                if self.flag_end : break
                                sleep(1-(time() % 1))
                else:
                        return

#================================ for test ===============================================

def main():
        parser = redis_parser('B', None, 'redis_parser')
        if parser == None : return
        parser.start()
        parser.wait_for_start()
        parser.join()

if __name__ == "__main__":
        try:
                main()
        except KeyboardInterrupt:
                pass
        except:
                print_exc()
        finally:
                print()

