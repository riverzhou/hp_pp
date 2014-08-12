#!/usr/bin/env python3

from socketserver       import UDPServer, BaseRequestHandler
from time               import time, sleep, localtime, mktime, strptime, strftime
from struct             import pack, unpack
from traceback          import print_exc
from hashlib            import md5
from xml.etree          import ElementTree
from threading          import Thread, Event, Lock, Semaphore

from pp_baseclass       import pp_thread, pp_sender
from pp_config          import pp_config
from pp_db              import mysql_db
from pp_log             import logger, printer

#-------------------------------------------

UDP_SERVER =('0.0.0.0', 999)

Thread.daemon  = True
UDPServer.allow_reuse_address = True
UDPServer.request_queue_size  = 100

price_limit   = 72600
number_limit  = 7400
number_people = 135000

#================================================================================

def time_sub(end, begin):
        return int(mktime(strptime('1970-01-01 '+end, '%Y-%m-%d %H:%M:%S'))) - int(mktime(strptime('1970-01-01 '+begin, '%Y-%m-%d %H:%M:%S')))

def time_add(time, second):
        ret = strftime('%Y-%m-%d %H:%M:%S', localtime(int(mktime(strptime('1970-01-01 '+time, "%Y-%m-%d %H:%M:%S"))) + second))
        return ret.split()[1]

def getsleeptime(itime):
        return itime - time()%itime

def read_mysql2list(date, begin, end, mode):
        global pp_config
        mysql = mysql_db(pp_config['mysql_format_db'])
        if mode == 'price':
                prefix = 'format_price_'
        elif mode == 'number':
                prefix = 'format_number_'
        else:
                return None
        table = prefix + date.replace('-','_')
        list_data = mysql.read(table)
        list_out = []
        for data in list_data:
                time = str(data[1]).split()[1]
                if time_sub(time, begin) >= 0 and time_sub(end, time) >= 0:
                        list_out.append(data)
        mysql.close()
        return list_out

def create_time(begin, end):
        list_out = []
        number = time_sub(end, begin)
        for i in range(number):
                time = time_add(begin, i)
                list_out.append(time)
        return list_out

def format_data(list_data):
        list_out = []
        for data in list_data :
                list_out.append((str(data[1]).split()[1], str(data[2])))
        return list_out

#================================================================================

class proto_udp():
        def decode(self, data):
                buff = b''
                len0 = len(data)
                len1 = len0 // 4
                len2 = len0 % 4
                if len2 != 0:
                        len1 += 1
                for i in range(4 - len2):
                        data += b'0'
                for i in range(len1) :
                        buff += pack('i', ~unpack('i', data[i*4:i*4+4])[0])
                buff = buff[0:len0]
                return buff

        def encode(self, data):
                buff = b''
                len0 = len(data)
                len1 = len0 // 4
                len2 = len0 % 4
                if len2 != 0:
                        len1 += 1
                for i in range(4 - len2):
                        data += b'0'
                for i in range(len1) :
                        buff += pack('i', ~unpack('i', data[i*4:i*4+4])[0])
                buff = buff[0:len0]
                return buff

        def udp_make_format_ack(self, key_val):
                return ( (
                        '<xml><TYPE>FORMAT</TYPE><INFO>\r\n' +
                        '拍卖会：%1%\r\n' +
                        '投放额度数：%2%\r\n' +
                        '本场拍卖会警示价：%3%\r\n' +
                        '拍卖会起止时间：%4%至%5%\r\n' +
                        '首次出价时段：%6%至%7%\r\n' +
                        '修改出价时段：%8%至%9%\r\n' +
                        '\r\n' +
                        '          目前为首次出价时段\r\n' +
                        '系统目前时间：%10%\r\n' +
                        '目前已投标人数：%11%\r\n' +
                        '目前最低可成交价：%12%\r\n' +
                        '最低可成交价出价时间：%13%\r\n' +
                        '#\r\n' +
                        '拍卖会：%1%\r\n' +
                        '投放额度数：%2%\r\n' +
                        '目前已投标人数：%3%\r\n' +
                        '拍卖会起止时间：%4%至%5%\r\n' +
                        '首次出价时段：%6%至%7%\r\n' +
                        '修改出价时段：%8%至%9%\r\n' +
                        '\r\n' +
                        '          目前为修改出价时段\r\n' +
                        '系统目前时间：%10%\r\n' +
                        '目前最低可成交价：%11%\r\n' +
                        '最低可成交价出价时间：%12%\r\n' +
                        '目前修改价格区间：%13%至%14%</INFO><xml>'
                        ).encode('gb18030') ,
                        key_val['addr']
                        )

        def parse_ack(self, string):
                key_val = {}
                try:
                        xml_string = '<XML>' + string.strip() + '</XML>'
                        root = ElementTree.fromstring(xml_string)
                        for child in root:
                                key_val[child.tag] = child.text
                except :
                        print(string)
                print(string)
                #print(sorted(key_val.items()))
                #print('')
                return key_val


        def udp_make_x_info(self, key_val):
                '''
                <TYPE>INFO</TYPE><INFO>C2014年5月24日上海市个人非营业性客车额度投标拍卖会尚未开始。
                起止时间为：
                2014年5月24日10时30分0秒
                到2014年5月24日11时30分0秒

                系统目前时间：10:20:06</INFO>
                '''
                info = ( (
                        '<TYPE>INFO</TYPE><INFO>C%s上海市个人非营业性客车额度投标拍卖会尚未开始。\r\n起止时间为：\r\n%s10时30分0秒\r\n到%s11时30分0秒\r\n\r\n系统目前时间：%s</INFO>'
                        ) % (
                        key_val['date'],
                        key_val['date'],
                        key_val['date'],
                        key_val['systime']
                        ) )
                print(info)
                return info.encode('gb18030')

        def udp_make_y_info(self, key_val):
                '''
                <TYPE>INFO</TYPE><INFO>C2014年5月24日上海市个人非营业性客车额度投标拍卖会已经结束，稍后发布拍卖会结果，请等待！


                拍卖会结果也可通过本公司网站WWW.ALLTOBID.COM进行查询。</INFO>
                '''
                info = ( (
                        '<TYPE>INFO</TYPE><INFO>C%s上海市个人非营业性客车额度投标拍卖会已经结束，稍后发布拍卖会结果，请等待！\r\n\r\n拍卖会结果也可通过本公司网站WWW.ALLTOBID.COM进行查询。</INFO>'
                        ) % (
                        key_val['date']
                        ) )
                print(info)
                return info.encode('gb18030')

        def udp_make_a_info(self, key_val):
                '''
                <TYPE>INFO</TYPE><INFO>A2014年5月24日上海市个人非营业性客车额度投标拍卖会^7400^72600^10:30^11:30^10:30^11:00^11:00^11:30^10:30:13^8891^72600^10:30:13</INFO>
                '''
                info = ( (
                        '<TYPE>INFO</TYPE><INFO>A%s上海市个人非营业性客车额度投标拍卖会^%s^%s^10:30^11:30^10:30^11:00^11:00^11:30^%s^%s^%s^%s</INFO>'
                        ) % (
                        key_val['date'],
                        key_val['number_limit'],
                        key_val['price_limit'],
                        key_val['systime'],
                        key_val['number'],
                        key_val['price'],
                        key_val['lowtime']
                        ) )
                print(info)
                return info.encode('gb18030')

        def udp_make_b_info(self, key_val):
                '''
                <TYPE>INFO</TYPE><INFO>B2014年5月24日上海市个人非营业性客车额度投标拍卖会^7400^114121^10:30^11:30^10:30^11:00^11:00^11:30^11:00:14^72600^10:30:12^72300^72900</INFO>
                '''
                info = ( (
                        '<TYPE>INFO</TYPE><INFO>B%s上海市个人非营业性客车额度投标拍卖会^%s^%s^10:30^11:30^10:30^11:00^11:00^11:30^%s^%s^%s^%s^%s</INFO>'
                        ) % (
                        key_val['date'],
                        key_val['number_limit'],
                        key_val['number'],
                        key_val['systime'],
                        key_val['price'],
                        key_val['lowtime'],
                        str(int(key_val['price']) - 300),
                        str(int(key_val['price']) + 300),
                        ) )
                print(info)
                return info.encode('gb18030')

#------------------------------------------------------

class info_maker(pp_thread, proto_udp):
        #strftime('%H:%M:%S',localtime(time()))
        def __init__(self, info = ''):
                global pp_config
                pp_thread.__init__(self, info)
                proto_udp.__init__(self)
                self.addr_list = []
                self.lock_addr = Lock()
                self.time_x = time_sub(pp_config['udp_before_end'], pp_config['udp_before_begin'])
                self.time_y = time_sub(pp_config['udp_after_end'], pp_config['udp_after_begin'])
                self.time_a = time_sub(pp_config['udp_first_end'], pp_config['udp_first_begin'])
                self.time_b = time_sub(pp_config['udp_second_end'], pp_config['udp_second_begin'])
                self.list_data_x = create_time(pp_config['udp_before_begin'], pp_config['udp_before_end'])
                self.list_data_y = create_time(pp_config['udp_after_begin'], pp_config['udp_after_end'])
                self.list_data_a = format_data(read_mysql2list(pp_config['udp_date'], pp_config['udp_first_begin'], pp_config['udp_first_end'], 'number'))
                self.list_data_b = format_data(read_mysql2list(pp_config['udp_date'], pp_config['udp_second_begin'], pp_config['udp_second_end'], 'price'))
                self.date   = '%s年%s月%s日' % tuple(pp_config['udp_date'].split('-'))

        def main(self):
                while True:
                        count = 0
                        while count < self.time_x :
                                if self.make_x(count) == True : count += 1
                                sleep(getsleeptime(1))

                        count = 0
                        while count < self.time_a :
                                if self.make_a(count) == True : count += 1
                                sleep(getsleeptime(1))

                        count = 0
                        while count < self.time_b :
                                if self.make_b(count) == True : count += 1
                                sleep(getsleeptime(1))

                        count = 0
                        while count < self.time_y :
                                if self.make_y(count) == True : count += 1
                                sleep(getsleeptime(1))

                        break

        def make_x(self, count):
                if len(self.addr_list) == 0 :
                        return False
                key_val = {}
                key_val['systime']  = self.list_data_x[count]
                key_val['date']     = self.date
                self.make(self.udp_make_x_info(key_val))
                return True

        def make_y(self, count):
                if len(self.addr_list) == 0 :
                        return False
                key_val = {}
                key_val['systime']  = self.list_data_y[count]
                key_val['date']     = self.date
                self.make(self.udp_make_y_info(key_val))
                return True

        def make_a(self, count):
                global price_limit, number_limit
                if len(self.addr_list) == 0 :
                        return False
                key_val = {}
                key_val['systime']  = self.list_data_a[count][0]
                key_val['lowtime']  = self.list_data_a[count][0]
                key_val['number']   = self.list_data_a[count][1]
                key_val['price']    = price_limit
                key_val['date']     = self.date
                key_val['number_limit'] = number_limit
                key_val['price_limit']  = price_limit
                self.make(self.udp_make_a_info(key_val))
                return True

        def make_b(self, count):
                global number_people, number_limit
                if len(self.addr_list) == 0 :
                        return False
                key_val = {}
                key_val['systime']  = self.list_data_b[count][0]
                key_val['lowtime']  = self.list_data_b[count][0]
                key_val['number']   = number_people
                key_val['price']    = self.list_data_b[count][1]
                key_val['date']     = self.date
                key_val['number_limit'] = number_limit
                self.make(self.udp_make_b_info(key_val))
                return True

        def make(self, info):
                addr_list = []
                self.lock_addr.acquire()
                for addr in self.addr_list :
                        addr_list.append(addr)
                self.lock_addr.release()
                for addr in addr_list :
                        daemon_bs.put((info, addr))

        def reg(self, addr):
                self.lock_addr.acquire()
                if not addr in self.addr_list :
                        self.addr_list.append(addr)
                self.lock_addr.release()

        def unreg(self, addr):
                self.lock_addr.acquire()
                for i in range(len(self.addr_list)) :
                        if self.addr_list[i] == addr :
                                del(self.addr_list[i])
                                break
                self.lock_addr.release()

#------------------------------------------------------

class buff_sender(pp_sender):
        def proc(self, buff):  # buff 为 (info, addr)
                global server_udp, daemon_im
                info, addr = buff
                data = daemon_im.encode(info)
                server_udp.socket.sendto(data, addr)

#------------------------------------------------------

class udp_handle(BaseRequestHandler):
        def handle(self):
                global daemon_im
                proto_dict = {
                        'FORMAT' : self.proc_format ,
                        'LOGOFF' : self.proc_logoff ,
                        }
                string = self.get()
                key_val = daemon_im.parse_ack(string)
                key_val['addr'] = self.client_address
                try:
                        proc = proto_dict[key_val['TYPE']]
                except  KeyError:
                        pass
                except:
                        print_exc()
                else:
                        proc(key_val)

        def get(self):
                global daemon_im
                return daemon_im.decode(self.request[0]).decode('gb18030')

        def proc_logoff(self, key_val):
                global daemon_im
                daemon_im.unreg(key_val['addr'])

        def proc_format(self, key_val):
                global daemon_im, daemon_bs
                daemon_im.reg(key_val['addr'])
                daemon_bs.put(daemon_im.udp_make_format_ack(key_val))

#================================================================================

def main():
        global daemon_im, daemon_bs, server_udp
        daemon_im = info_maker()
        daemon_im.start()
        daemon_im.wait_for_start()
        daemon_bs = buff_sender()
        daemon_bs.start()
        daemon_bs.wait_for_start()
        server_udp = UDPServer(UDP_SERVER, udp_handle)
        logger.debug('UDP Server start at %s : %d' % (UDP_SERVER[0], UDP_SERVER[1]))
        server_udp.serve_forever()

if __name__ == "__main__":
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()
        finally:
                print()


