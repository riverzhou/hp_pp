#!/usr/bin/env python3

#==========================================================

from socket             import gethostbyname

from pp_log             import logger, printer
from pp_sslworker       import pyget
from pp_sslproto        import *
from pp_server          import server_dict

#==========================================================

pyget_machinecode  = ''                  # 为空串表示自动生成随机特征码
pyget_loginimage   = ''

#==========================================================

def proc_login(arg_val):
        global pyget_machinecode, pyget_loginimage, server_dict

        bidno   = arg_val['bidno']
        passwd  = arg_val['passwd']
        group   = arg_val['group']
        
        machine = proto_machine(pyget_machinecode, pyget_loginimage)
        pyget_machinecode       = machine.mcode

        key_val = {}
        key_val['bidno']        = bidno
        key_val['passwd']       = passwd
        key_val['mcode']        = machine.mcode
        key_val['login_image']  = machine.image
        key_val['host_name']    = server_dict[group]['login']['name']
        key_val['host_ip']      = server_dict[group]['login']['ip']
        key_val['host_port']    = server_dict[group]['login']['port']

        login_server = key_val['host_name']

        proto    = proto_ssl_login(key_val)
        info_val = pyget(login_server, proto.make_login_req(), proto.make_ssl_head())
        #logger.debug(sorted(info_val.items()))

        if info_val['status'] != 200 :
                logger.error('ack status error!!!')
                logger.error(sorted(info_val.items()))
                logger.error(info_val['body'].decode())
                return

        ack_sid  = proto.get_sid_from_head(info_val['head'])
        ack_val  = proto.parse_login_ack(info_val['body'])
        ack_val['sid'] = ack_sid
        logger.debug(sorted(ack_val.items()))

        return ack_val

def proc_image(arg_val):
        global pyget_machinecode, pyget_loginimage

        bidno    = arg_val['bidno']
        price    = arg_val['price']
        group    = arg_val['group']

        machine = proto_machine(pyget_machinecode, pyget_loginimage)

        key_val = {}
        key_val['bidno']        = bidno
        key_val['mcode']        = machine.mcode
        key_val['login_image']  = machine.image
        key_val['host_name']    = server_dict[group]['toubiao']['name']
        key_val['host_ip']      = server_dict[group]['toubiao']['ip']
        key_val['host_port']    = server_dict[group]['toubiao']['port']

        image_server = key_val['host_name']

        proto    = proto_ssl_image(key_val)
        info_val = pyget(image_server, proto.make_image_req(price), proto.make_ssl_head())
        #logger.debug(sorted(info_val.items()))

        if info_val['status'] != 200 :
                logger.error('ack status error!!!')
                logger.error(sorted(info_val.items()))
                logger.error(info_val['body'].decode())
                return

        ack_sid  = proto.get_sid_from_head(info_val['head'])
        ack_val  = proto.parse_image_ack(info_val['body'])
        ack_val['sid']   = ack_sid
        ack_val['price'] = price
        #logger.debug(sorted(ack_val.items()))
        logger.debug(ack_sid)

        return ack_val

def proc_price(arg_val):
        global pyget_machinecode, pyget_loginimage

        bidno     = arg_val['bidno']
        price     = arg_val['price']
        image     = arg_val['image']
        passwd    = arg_val['passwd']
        image_sid = arg_val['sid']
        group     = arg_val['group']

        machine = proto_machine(pyget_machinecode, pyget_loginimage)

        key_val = {}
        key_val['bidno']        = bidno
        key_val['mcode']        = machine.mcode
        key_val['passwd']       = passwd
        key_val['login_image']  = machine.image
        key_val['host_name']    = server_dict[group]['toubiao']['name']
        key_val['host_ip']      = server_dict[group]['toubiao']['ip']
        key_val['host_port']    = server_dict[group]['toubiao']['port']

        price_server = key_val['host_name']

        if image_sid == None :
                debug.error('no image_sid')
                return

        proto    = proto_ssl_price(key_val)
        info_val = pyget(price_server, proto.make_price_req(price, image), proto.make_ssl_head(image_sid))
        #logger.debug(sorted(info_val.items()))
        logger.debug(proto.make_ssl_head(image_sid))

        if info_val['status'] != 200 :
                logger.error('ack status error!!!')
                logger.error(sorted(info_val.items()))
                logger.error(info_val['body'].decode())
                return

        ack_sid  = proto.get_sid_from_head(info_val['head'])
        ack_val  = proto.parse_price_ack(info_val['body'])
        ack_val['sid'] = ack_sid
        logger.debug(sorted(ack_val.items()))

        return ack_val


