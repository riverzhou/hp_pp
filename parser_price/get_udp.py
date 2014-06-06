#!/usr/bin/env python

from sys     import argv
from struct  import pack, unpack

import dpkt

counter    = 0
ipcounter  = 0
udpcounter = 0

if len(argv) != 2 :
        print './get_udp.py   name.pcap'
        exit()

try:
        pcap  = open(argv[1], 'r')
except :
        raise SystemExit

req   = open('udp.req', 'ab')
ack   = open('udp.ack', 'ab')

for ts, pkt in dpkt.pcap.Reader(pcap):
        counter += 1
        eth = dpkt.ethernet.Ethernet(pkt) 
        if eth.type != dpkt.ethernet.ETH_TYPE_IP: 
                continue

        ip = eth.data
        ipcounter += 1

        if ip.p == dpkt.ip.IP_PROTO_UDP:
                #print('sport %d , dport %d , ulen %d' % (ip.data.sport, ip.data.dport, ip.data.ulen))
                udpcounter += 1
                if ip.data.sport == 999 :
                        ack.write(pack('i', len(bytes(ip.data.data))))
                        ack.write(bytes(ip.data.data))

                if ip.data.dport == 999 :
                        req.write(pack('i', len(bytes(ip.data.data))))
                        req.write(bytes(ip.data.data))

ack.close()
req.close()

print "Total number of eth packets: ", counter
print "Total number of ip  packets: ", ipcounter
print "Total number of udp packets: ", udpcounter

