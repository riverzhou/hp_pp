#!/usr/bin/env python3

from socketserver       import UDPServer, BaseRequestHandler
from time               import time, localtime, strftime, sleep
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

#================================================================================
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
                        printer.error(string)
                printer.info(string)
                printer.error(sorted(key_val.items()))
                printer.error('')
                return key_val

        def udp_make_a_info(self, key_val):
                '''
                <TYPE>INFO</TYPE><INFO>A2014年5月24日上海市个人非营业性客车额度投标拍卖会^7400^72600^10:30^11:30^10:30^11:00^11:00^11:30^10:30:13^8891^72600^10:30:13</INFO>
                '''
                info = ( (
                        '<TYPE>INFO</TYPE><INFO>A2014年5月24日上海市个人非营业性客车额度投标拍卖会^7400^72600^10:30^11:30^10:30^11:00^11:00^11:30^%s^%s^%s^%s</INFO>'
                        ) % (
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
                        '<TYPE>INFO</TYPE><INFO>B2014年5月24日上海市个人非营业性客车额度投标拍卖会^7400^%s^10:30^11:30^10:30^11:00^11:00^11:30^%s^%s^%s^%s^%s</INFO>'
                        ) % (
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
                pp_thread.__init__(self, info)
                proto_udp.__init__(self)
                self.addr_list = []
                self.lock_addr = Lock()
                self.number = 0
                self.price  = 100

        def main(self):
                time_a = 600            # 上半场持续时间（秒）
                time_b = 600            # 下半场持续时间（秒）
                while True:
                        count = 0
                        while count < time_a :
                                self.make_a(count)
                                count += 1
                                sleep(1)
                        count = 0
                        while count < time_b :
                                self.make_b(count)
                                count += 1
                                sleep(1)

        def make_a(self, count):
                if len(self.addr_list) == 0 :
                        return
                key_val = {}
                key_val['systime']   = strftime('%H:%M:%S',localtime(time()))
                key_val['lowtime']   = strftime('%H:%M:%S',localtime(time()))
                key_val['number']    = self.number
                key_val['price']     = self.price
                self.number += 1
                self.price  += 100
                self.proc(self.udp_make_a_info(key_val))

        def make_b(self, count):
                if len(self.addr_list) == 0 :
                        return
                key_val = {}
                key_val['systime']   = strftime('%H:%M:%S',localtime(time()))
                key_val['lowtime']   = strftime('%H:%M:%S',localtime(time()))
                key_val['number']    = self.number
                key_val['price']     = self.price
                self.number += 1
                self.price  += 100
                self.proc(self.udp_make_b_info(key_val))

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
                proto_dict = {
                        'FORMAT' : self.proc_format ,
                        'LOGOFF' : self.proc_logoff ,
                        }
                string = self.get()
                key_val = proto_udp.parse_ack(string)
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
                return proto_udp.decode(self.request[0]).decode('gb18030')

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


