#!/usr/bin/env python3

#==========================================================

from socket             import gethostbyname

from pp_log             import logger, printer
from pp_sslworker       import pyget
from pp_sslproto        import *

#==========================================================

pyget_machinecode  = ''                  # 为空串表示自动生成随机特征码
pyget_loginimage   = ''

#==========================================================

def main_init_dns(group):
        global login_server, price_server, image_server, pyget_server_group, pp_server_dict, pp_server_dict_2
        server_dict = pp_server_dict if group == 0 else pp_server_dict_2
        login_server = server_dict['login'][0]
        image_server = server_dict['toubiao'][0]
        price_server = server_dict['toubiao'][0]

def proc_login(arg_val):
        global pyget_machinecode, pyget_loginimage

        bidno  = arg_val['bidno']
        passwd = arg_val['passwd']
        
        machine = proto_machine(pyget_machinecode, pyget_loginimage)
        pyget_machinecode       = machine.mcode

        key_val = {}
        key_val['bidno']        = bidno
        key_val['passwd']       = passwd
        key_val['mcode']        = machine.mcode
        key_val['login_image']  = machine.image
        key_val['host_name']    = login_server
        key_val['host_ip']      = gethostbyname(login_server)

        proto    = proto_ssl_login(key_val)
        info_val = pyget(login_server, proto.make_login_req(), proto.make_ssl_head())
        #logger.debug(sorted(info_val.items()))

        if info_val['status'] != 200 :
                logger.error('ack status error!!!')
                logger.error(sorted(info_val.items()))
                return

        ack_sid  = proto.get_sid_from_head(info_val['head'])
        ack_val  = proto.parse_login_ack(info_val['body'])
        ack_val['sid'] = ack_sid
        logger.debug(sorted(ack_val.items()))

        return ack_val

def proc_image(arg_val):
        global pyget_machinecode, pyget_loginimage

        bidno   = arg_val['bidno']
        price   = arg_val['price']

        machine = proto_machine(pyget_machinecode, pyget_loginimage)

        key_val = {}
        key_val['bidno']        = bidno
        key_val['mcode']        = machine.mcode
        key_val['login_image']  = machine.image
        key_val['host_name']    = image_server
        key_val['host_ip']      = gethostbyname(image_server)

        proto    = proto_ssl_image(key_val)
        info_val = pyget(image_server, proto.make_image_req(price), proto.make_ssl_head())
        #logger.debug(sorted(info_val.items()))

        if info_val['status'] != 200 :
                logger.error('ack status error!!!')
                logger.error(sorted(info_val.items()))
                return

        ack_sid  = proto.get_sid_from_head(info_val['head'])
        ack_val  = proto.parse_image_ack(info_val['body'])
        ack_val['sid'] = ack_sid
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

        machine = proto_machine(pyget_machinecode, pyget_loginimage)

        key_val = {}
        key_val['bidno']        = bidno
        key_val['mcode']        = machine.mcode
        key_val['passwd']       = passwd
        key_val['login_image']  = machine.image
        key_val['host_name']    = image_server
        key_val['host_ip']      = gethostbyname(image_server)

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
                return

        ack_sid  = proto.get_sid_from_head(info_val['head'])
        ack_val  = proto.parse_price_ack(info_val['body'])
        ack_val['sid'] = ack_sid
        logger.debug(sorted(ack_val.items()))

        return ack_val


