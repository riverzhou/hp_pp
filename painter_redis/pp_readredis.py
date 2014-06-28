#!/usr/bin/env python3

from    threading       import Thread, Event, Lock, Semaphore
from    queue           import Queue, LifoQueue
from    redis           import StrictRedis
from    traceback       import print_exc
from    pickle          import dumps, loads
from    time            import sleep, time, localtime, mktime, strptime, strftime

from    pp_baseclass    import pp_thread
from    pp_config       import pp_config

#=========================================================================================

class redis_reader(pp_thread):
        key_name = pp_config['redis_key']

        def __init__(self, output=None, info=None):
                pp_thread.__init__(self, info)
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
                except KeyboardInterrupt:
                        raise KeyboardInterrupt
                except:
                        print_exc()
                        return None

        def main(self):
                while True:
                        redis_info = self.get_info()
                        if redis_info == None : break
                        time, key_val = loads(redis_info[1])
                        #time = time.split(' ')[1].split('.')[0]
                        #print(key_val)
                        if self.output != None : self.output.put(key_val)

class redis_parser(pp_thread):
        def __init__(self, output=None, info=None):
                pp_thread.__init__(self, info)
                self.output = output

                self.origin_data_a = []
                self.origin_data_b = []
                self.lock_data_a   = Lock()
                self.lock_data_b   = Lock()

                self.result_data_a  = ([],[],[])
                self.result_data_b  = ([],[],[])
                self.result_count_a = 0
                self.result_count_b = 0

                self.reader = redis_reader(self, 'redis_reader')
                if self.reader == None : return None

                self.reader.start()
                self.reader.wait_for_start()

        def put(self, info):
                try:
                        code = info['code']
                except:
                        print('code error')
                        return
                if code == 'A' :
                        self.lock_data_a.acquire()
                        self.origin_data_a.append(info)
                        self.lock_data_a.release()
                elif code == 'B' :
                        self.lock_data_b.acquire()
                        self.origin_data_b.append(info)
                        self.lock_data_b.release()
                else:
                        print('unknow code')

        def sub_time(self, time2, time1):
                return int(mktime(strptime(time2, "%H:%M:%S"))) - int(mktime(strptime(time1, "%H:%M:%S")))
        
        def add_time(self, time):
                return strftime("%H:%M:%S", localtime(int(mktime(strptime(time, "%H:%M:%S"))) + 1))

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
                self.result_data_b[2].append(result[0])
                self.result_data_b[1].append(result[1])
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

        def proc(self):
                if len(self.origin_data_b) == 0 :
                        self.clear_data_a()
                        self.parse_data_a()
                        self.send_result_a()
                else:
                        self.clear_data_b()
                        self.parse_data_b()
                        self.send_result_b()

        def main(self):
                while True:
                        self.proc()
                        sleep(time() % 1)

#================================ for test ===============================================

def main():
        parser = redis_parser(None,'redis_parser')
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

