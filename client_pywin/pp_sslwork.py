#!/usr/bin/env python3

from http.client    import HTTPSConnection, HTTPConnection
from time           import sleep
from socket         import timeout as sock_timeout
from time           import strftime, localtime, time
from traceback      import print_exc

def pyget(host, req, headers = {}, timeout = None):
        while True:
                handler = HTTPSConnection(host, timeout = timeout)
                handler._http_vsn = 10
                handler._http_vsn_str = 'HTTP/1.0' 
                try:
                        handler.connect()
                except (sock_timeout, TimeoutError):
                        handler.close()
                        continue
                except:
                        print_exc()
                        continue
                break
        #--------------------------------------------------------
        try:
                handler.request('GET', req, headers = headers)
        except:
                handler.close()
                print_exc()
                return None
        try:
                ack  = handler.getresponse()
                body = ack.read()
        except:
                handler.close()
                print_exc()
                return None
        #--------------------------------------------------------
        handler.close()

        key_val = {}
        key_val['body']    = body
        key_val['head']    = str(ack.msg)
        key_val['status']  = ack.status

        return key_val

if __name__ == '__main__' :
        login_req  = '/car/gui/login.aspx?BIDNUMBER=12345678&BIDPASSWORD=1234&MACHINECODE=ABCDEFGHI&CHECKCODE=d457df935057803ab4a610710bd3d4c6&VERSION=177&IMAGENUMBER=157326'
        image_req  = '/car/gui/imagecode.aspx?BIDNUMBER=12345678&BIDPASSWORD=1234&BIDAMOUNT=74000&VERSION=177&CHECKCODE=e83fa61d212330f8e95f0e3af0542ef8'
        price_req  = '/car/gui/bid.aspx?BIDNUMBER=12345678&BIDPASSWORD=1234&BIDAMOUNT=74000&MACHINECODE=ABCDEFGHI&CHECKCODE=bd2c153421adb0d8daf18cbb703299a2&VERSION=177&IMAGENUMBER=708270'
        host = '192.168.1.108'
        ret = pyget(host, login_req)
        print(ret['status'])
        print(ret['head'])
        print(ret['body'])


