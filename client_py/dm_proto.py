#!/usr/bin/env python3

from abc                        import ABCMeta, abstractmethod
from threading                  import Thread
from multiprocessing            import Process, Event, Condition, Lock, Event
from struct                     import pack, unpack
from socketserver               import TCPServer, BaseRequestHandler
from socket                     import socket
from traceback                  import print_exc
from time                       import time, localtime, strftime
from hashlib                    import md5
from time                       import sleep
from socket                     import socket, gethostbyname, AF_INET, SOCK_STREAM, SOCK_DGRAM


class dm_handler(BaseRequestHandler):
        def handle(self):
                pass



class proto_dm():
        def __init__(self):
                pass


