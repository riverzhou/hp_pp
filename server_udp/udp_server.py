#!/usr/bin/env python3
#coding=UTF-8

from struct             import pack, unpack
from socketserver       import UDPServer, BaseRequestHandler  
from traceback          import print_exc
from time               import time, localtime, strftime
from hashlib            import md5

HOST    = ''
PORT    = 999
BUFSIZE = 65535


ps_id           = '332627197611242029'

id_dict         = {}

user_dict       = {}

class user():
        def __init__(self, uid):
                if not uid in id_dict:
                        id_dict[uid] = ps_id

                self.order          = ('FORMAT','INFO','MSG','RELOGIN','ADDSERV','MARQUEE')
                self.ack            = {}
                #self.ack['INFO']   = '<TYPE>INFO</TYPE><BIDNO>98765432</BIDNO><VCODE>7AD4010132285769C8496849089947CA</VCODE>'
                self.ack['INFO']    =    '<TYPE>INFO</TYPE><BIDNO>'+uid+'</BIDNO><VCODE>'+self.get_vcode(uid)+'</VCODE>'
                self.ack['FORMAT']  =  '<TYPE>FORMAT</TYPE><BIDNO>'+uid+'</BIDNO><VCODE>'+self.get_vcode(uid)+'</VCODE>'
                self.ack['MSG']     =     '<TYPE>MSG</TYPE><BIDNO>'+uid+'</BIDNO><VCODE>'+self.get_vcode(uid)+'</VCODE>'
                self.ack['RELOGIN'] = '<TYPE>RELOGIN</TYPE><BIDNO>'+uid+'</BIDNO><VCODE>'+self.get_vcode(uid)+'</VCODE>'
                self.ack['ADDSERV'] = '<TYPE>ADDSERV</TYPE><BIDNO>'+uid+'</BIDNO><VCODE>'+self.get_vcode(uid)+'</VCODE>'
                self.ack['MARQUEE'] = '<TYPE>MARQUEE</TYPE><BIDNO>'+uid+'</BIDNO><VCODE>'+self.get_vcode(uid)+'</VCODE>'
                self.req            = []
                self.req_parse      = []
                self.feq            = 0
                self.feq_test       = 2
                self.keys           = ('TYPE','BIDNO','VCODE')
                return

        def get_vcode(self, uid):
                return self.get_md5(id_dict[uid] + uid)

        def get_md5(self, string):
                return md5(string.encode()).hexdigest().upper()

        def upinfo(self, req):
                self.req.append(req)
                self.req_parse.append(user.get_val(self.keys,req))
                self.feq += 1 
                return

        def getack(self):
                feq = self.feq
                if feq > 5 :
                        feq = self.feq_test                                      

                return self.ack[self.order[feq]]

        @staticmethod                                      
        def update(req):
                bidno = user.get_bidno(req)

                print('bidno =', bidno)

                if not bidno in user_dict:
                        user_dict[bidno] = user(bidno)

                user_dict[bidno].upinfo(req)
                return user_dict[bidno]                                      

        @staticmethod
        def get_bidno(req):
                return user.get_val(['BIDNO'], req)['BIDNO']

        @staticmethod
        def get_val(keys, txt):
                result = {}
                buff   = txt.decode()
                for k in keys:
                        head = '<' + k + '>'
                        end  = '</' + k + '>'
                        h = buff.find(head) + len(head)
                        e = buff.find(end)
                        result[k] = buff[h:e]
                return result


class MyBaseRequestHandlerr(BaseRequestHandler):  
        def __init__(self, request, client_address, server):
                self.my_init()
                BaseRequestHandler.__init__(self, request, client_address, server)
                return

        def my_init(self):
                self.user = ''
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
                print()
                buff    = self.request[0]
                socket  = self.request[1]
                if( not buff) :
                        return False
                req = self.decode_data(buff)
                print(strftime('%H:%M:%S',localtime(time())), self.client_address)
                self.user_update(req)
                print(req.decode())
                return True

        def send_data(self):
                ack     = self.user_getack()
                buff    = self.encode_data(str.encode(ack))
                socket  = self.request[1]
                socket.sendto(buff, self.client_address)
                print(ack)
                self.print_bytes(buff)
                print()
                return True

        def print_bytes(self, buff):
                out     = ''
                for b in buff:
                        out += hex(b)
                        out += ' '
                print(out)

        def user_update(self, buff):
                self.user = user.update(buff)
                return 

        def user_getack(self):
                return self.user.getack()


if __name__ == "__main__": 
        server = UDPServer((HOST, PORT), MyBaseRequestHandlerr)
        server.allow_reuse_address = True
        server.serve_forever() 



