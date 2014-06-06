#!/usr/bin/env python3

from struct     import pack, unpack, pack_into, unpack_from

def sub_time(time2, time1):
        h1 , m1, s1 = time1.split(':')
        h2 , m2, s2 = time2.split(':')
        h1 , m1, s1 = int(h1), int(m1), int(s1)
        h2 , m2, s2 = int(h2), int(m2), int(s2)
        if h2 < h1 : h2 += 24
        return (h2-h1)*3600 + (m2-m1)*60 + (s2-s1)

def add_time(time):
        h , m, s = time.split(':')
        h , m, s = int(h), int(m), int(s)
        s += 1
        if s == 60 :
                s = 0
                m += 1
                if m == 60 :
                        m = 0
                        h += 1
                        if h == 24 : 
                                h = 0
        return  ('%.2d:%.2d:%.2d' % (h,m,s))

def decode_ack(buff):
        len0 = len(buff)
        len1 = len0 // 4
        len2 = len0 % 4
        if len2 != 0: len1 += 1
        buff += b'\0\0\0\0'
        data = bytearray(len0 + 4)
        view = memoryview(data)
        buff = memoryview(buff)
        for i in range(len1) :
                offset = i*4
                pack_into('i', view, offset, ~unpack_from('i', buff, offset)[0])
        data = bytes(data[0:len0])
        return data

def parse_info_a(info):
        p1 = info.find('<INFO>') + len('<INFO>')
        p2 = info.find('</INFO>')
        info = info[p1:p2]
        info = info.split('^')
        return 'A',info[9],info[11],info[10], info[12]

def parse_info_b(info):
        p1 = info.find('<INFO>') + len('<INFO>')
        p2 = info.find('</INFO>')
        info = info[p1:p2]
        info = info.split('^')
        return 'B',info[9],info[10],info[11]

def parse_info(info):
        if '<TYPE>INFO</TYPE><INFO>A' in info : return parse_info_a(info)
        if '<TYPE>INFO</TYPE><INFO>B' in info : return parse_info_b(info)
        return None

def write_result_a(result, res):
        last_time   = None
        last_number = None
        for parse in result:
                if parse[0] != 'A' :  continue
                time   = parse[1]
                number = parse[3]
                if last_time == None :
                        last_time   = time
                        last_number = number
                        string = '%s - %s\n' % (time, number)
                        res.write(string.encode())
                        continue
                delta_time = sub_time(time, last_time)
                if delta_time <= 0 :
                        continue
                if delta_time >  1 :
                        lost_time = last_time
                        for i in range(delta_time - 1) :
                                lost_time = add_time(lost_time)
                                string = '%s - %s\n' % (lost_time, last_number)
                                res.write(string.encode())
                last_time   = time
                last_number = number
                string = '%s - %s\n' % (time, number)
                res.write(string.encode())
        return True

def write_result_b(result, res):
        last_time   = None
        last_price  = None
        for parse in result:
                if parse[0] != 'B' : continue
                time   = parse[1]
                price  = parse[2]
                if last_time == None :
                        last_time   = time
                        last_price  = price 
                        string = '%s - %s\n' % (time, price)
                        res.write(string.encode())
                        continue
                delta_time = sub_time(time, last_time)
                if delta_time <= 0 :
                        continue
                if delta_time >  1 :
                        lost_time = last_time
                        for i in range(delta_time - 1) :
                                lost_time = add_time(lost_time)
                                string = '%s - %s\n' % (lost_time, last_price)
                                res.write(string.encode())
                last_time   = time
                last_price  = price 
                string = '%s - %s\n' % (time, price)
                res.write(string.encode())
        return True

def parse_ack():
        ack   = open('udp.ack', 'rb')
        res_a = open('a.res', 'wb')
        res_b = open('b.res', 'wb')
        res   = res_a, res_b
        result = []
        while True:
                head = ack.read(4)
                #print(head)
                if not head : break
                head = unpack('i', head)[0]
                #print(head)
                body  = ack.read(head)
                info  = decode_ack(body).decode('gb18030').strip()
                parse = parse_info(info)
                if parse != None : result.append(parse)
                #if parse != None : print(parse)
        write_result_a(result, res_a)
        write_result_b(result, res_b)
        res_a.close()
        res_b.close()

if __name__ == '__main__' :
        parse_ack()
