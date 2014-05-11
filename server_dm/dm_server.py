#!/usr/bin/env python3
#coding=UTF-8

from struct       import pack, unpack
from socketserver import ThreadingTCPServer, BaseRequestHandler  
from traceback    import print_exc

HOST    = ''
#PORT    = 9999
PORT    = 2000
BUFSIZE = 65535

class MyBaseRequestHandlerr(BaseRequestHandler):  

        def __init__(self, request, client_address, server):
                self.my_init()
                BaseRequestHandler.__init__(self, request, client_address, server)
                return

        def my_init(self):
                self.pkglen     = 0
                self.proto      = 0
                self.imagelen   = 0
                self.image      = b''
                self.result     = 654321
                return

        def handle(self):  
                try: 
                        if( self.recv_head()   == False ):
                                return
                        if( self.recv_body()   == False ):
                                return
                        if( self.send_result() == False ):
                                return
                except: 
                        print_exc() 
                        return

        def recv_head(self):
                head_len = 10
                head = b''
                buff = b''
                recv = 0

                while(recv < head_len):
                        buff = self.request.recv(head_len - recv)
                        if not buff:
                                return False
                        head += buff
                        recv += len(buff)

                self.pkglen, self.proto, self.imagelen = unpack('=IHI', head)
                self.pkglen += 4

                print('pkglen =', self.pkglen, ' , proto =', self.proto, ' , imagelen =', self.imagelen)

                if( self.imagelen == 0 ) :
                        return False

                return True

        def recv_body(self):
                body = b''
                buff = b''
                recv = 0

                while(recv < self.imagelen):
                        buff = self.request.recv(self.imagelen - recv)
                        if not buff:
                                return False
                        body += buff
                        recv += len(buff)

                self.image = body

                #print('image :' , self.image )

                return True

        def send_result(self):
                buff = pack('=IHII', 10, 10001, 4, self.result)

                self.request.send(buff)

                return True


if __name__ == "__main__": 
        ThreadingTCPServer.allow_reuse_address = True
        server = ThreadingTCPServer((HOST, PORT), MyBaseRequestHandlerr)
        server.serve_forever() 
