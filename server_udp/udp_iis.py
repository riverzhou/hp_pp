#!/usr/bin/env python3

from http.client        import HTTPSConnection, HTTPConnection
from traceback          import print_exc

from pp_baseclass       import pp_sender

ip_iis_server = '192.168.1.206'

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

        def proto_sync(self, price, time):
                return '/udp.aspx?price=%s&time=%s' % (price, time)

        def reset(self):
                return self.put(self.proto_reset())

        def sync(self, price, time):
                return self.put(self.proto_sync(price, time))


