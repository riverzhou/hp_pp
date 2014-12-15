#!/usr/bin/env python3

from http.client        import HTTPSConnection, HTTPConnection
from traceback          import print_exc

from pp_baseclass       import pp_sender

ip_iis_server = '192.168.1.190'

class iis(pp_sender):
        def send(self, req):
                print('iis send req : ', req)
                global ip_iis_server
                handler = HTTPConnection(ip_iis_server)
                handler._http_vsn = 10
                handler._http_vsn_str = 'HTTP/1.0'
                try:
                        handler.connect()
                except:
                        print_exc()
                        return False
                try:
                        handler.request('GET', req)
                except:
                        print_exc()
                        return False
                try:
                        ack  = handler.getresponse()
                        body = ack.read()
                except:
                        print_exc()
                        return False

                if ack.status == 200:
                        return True
                else:
                        print('status : ', ack.status)
                        return False

        def proc(self, buff):
                return self.send(buff)

        def proto_reset(self):
                return '/Default.aspx'

        def proto_sync(self, key_val):
                code    = key_val['code']
                date    = key_val['date']
                try:
                        limit   = key_val['number_limit']
                except:
                        limit   = '0'
                try:
                        number  = key_val['number']
                except:
                        number  = '0'
                try:
                        price   = key_val['price']
                except:
                        price   = '0'
                try:
                        time    = key_val['systime']
                except:
                        time    = '00:00:00'
                return '/udp.aspx?code=%s&date=%s&limit=%s&number=%s&price=%s&time=%s' % (code, date, limit, number, price, time)

        def reset(self):
                return self.put(self.proto_reset())

        def sync(self, key_val):
                return self.put(self.proto_sync(key_val))


