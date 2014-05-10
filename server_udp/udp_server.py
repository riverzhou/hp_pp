#!/usr/bin/env python3
#coding=UTF-8

from struct       import pack, unpack
from socketserver import UDPServer, BaseRequestHandler  
from traceback    import print_exc

HOST    = ''
PORT    = 999
BUFSIZE = 65535

class MyBaseRequestHandlerr(BaseRequestHandler):  
        def __init__(self, request, client_address, server):
                self.my_init()
                BaseRequestHandler.__init__(self, request, client_address, server)
                return

        def my_init(self):
                self.info       = '<TYPE>INFO</TYPE><BIDNO>98765432</BIDNO>'
                self.user       = {}
                return

        def decode_data(self,data):
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

        def encode_data(self,data):
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

        def handle(self):  
                try: 
                        if( self.recv_data() == False ):
                                return

                        if( self.send_data() == False ):
                                return
                except: 
                        print_exc() 
                        return

        def recv_data(self):
                buff    = self.request[0]
                socket  = self.request[1]
                if( not buff) :
                        return False
                self.user[socket] = self.decode_data(buff)
                print(self.user[socket])
                return True

        def send_data(self):
                buff    = self.encode_data(str.encode(self.info))
                socket  = self.request[1]
                self.request[1].sendto(buff, self.client_address)
                return True


if __name__ == "__main__": 
        server = UDPServer((HOST, PORT), MyBaseRequestHandlerr)
        server.allow_reuse_address = True
        server.serve_forever() 
