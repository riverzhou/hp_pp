#!/usr/bin/env python3

from  socket                import gethostbyname

#==================================================================================================================

pp_server_dict = {
        'login'    : ('tblogin.alltobid.com',   443),
        'toubiao'  : ('toubiao.alltobid.com',   443),
        'result'   : ('tbresult.alltobid.com',  443),
        'query'    : ('tbquery.alltobid.com',   443),
        'udp'      : ('tbudp.alltobid.com',     999),
        }

pp_server_dict_2 = {
        'login'    : ('tblogin2.alltobid.com',  443),
        'toubiao'  : ('toubiao2.alltobid.com',  443),
        'result'   : ('tbresult2.alltobid.com', 443),
        'query'    : ('tbquery2.alltobid.com',  443),
        'udp'      : ('tbudp2.alltobid.com',    999),
        }

server_dict = {
        0 : pp_server_dict,
        1 : pp_server_dict_2,
        }

def pp_dns_init():
        global pp_server_dict, pp_server_dict_2
        for key in pp_server_dict :
                name = pp_server_dict[key][0]
                port = pp_server_dict[key][1]
                ip   = gethostbyname(pp_server_dict[key][0])
                pp_server_dict[key] = {
                        'name' : name ,
                        'port' : port ,
                        'ip'   : ip ,
                        }

        for key in pp_server_dict_2 :
                name = pp_server_dict_2[key][0]
                port = pp_server_dict_2[key][1]
                ip   = gethostbyname(pp_server_dict_2[key][0])
                pp_server_dict_2[key] = {
                        'name' : name ,
                        'port' : port ,
                        'ip'   : ip ,
                        }

#============================================================

if __name__ == '__main__':
        pp_dns_init()
        print('0:')
        for key in sorted(server_dict[0]):
                print('%s : %s ' % (key, server_dict[0][key]))
        print('1:')
        for key in sorted(server_dict[1]):
                print('%s : %s ' % (key, server_dict[1][key]))

