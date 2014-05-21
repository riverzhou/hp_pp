#!/usr/bin/env python3

import sys
sys.path.append('..')

#==========================================================

from pp_client import *

from pp_log    import logger, printer

from hashlib   import md5
from traceback import print_exc
import pickle

#----------------------------------------------------------

def test_login_normal():
        user = pp_user(test_user['bidno'], test_user['passwd'], None, server_dict, machine)
        user.client.login.do_shoot()

def test_image_normal():
        user = pp_user(test_user['bidno'], test_user['passwd'], None, server_dict, machine)
        user.client.bid[0].image.do_warmup()
        user.client.bid[0].image.do_shoot()

def test_price_normal():
        user = pp_user(test_user['bidno'], test_user['passwd'], None, server_dict, machine)
        user.client.bid[0].price.do_warmup()
        user.client.bid[0].price.do_shoot()

#---------------------------------------

def test_login_mac2():
        user = pp_user(test_user['bidno'], test_user['passwd'], None, server_dict, machine2)
        user.client.login.do_shoot()

def test_image_mac2():
        user = pp_user(test_user['bidno'], test_user['passwd'], None, server_dict, machine2)
        user.client.bid[0].image.do_warmup()
        user.client.bid[0].image.do_shoot()

def test_price_mac2():
        user = pp_user(test_user['bidno'], test_user['passwd'], None, server_dict, machine2)
        user.client.bid[0].price.warmup()
        user.client.bid[0].price.do_shoot()

#---------------------------------------

def test_login_ccerr():
        global flag_fake_cc
        flag_fake_cc = True
        user = pp_user(test_user['bidno'], test_user['passwd'], None, server_dict, machine2)
        user.client.login.do_shoot()

def test_image_ccerr():
        global flag_fake_cc
        flag_fake_cc = True
        user = pp_user(test_user['bidno'], test_user['passwd'], None, server_dict, machine2)
        user.client.bid[0].image.do_warmup()
        user.client.bid[0].image.do_shoot()

def test_price_ccerr():
        global flag_fake_cc
        flag_fake_cc = True
        user = pp_user(test_user['bidno'], test_user['passwd'], None, server_dict, machine2)
        user.client.bid[0].price.do_warmup()
        user.client.bid[0].price.do_shoot()

#---------------------------------------

def test_login_vrerr():
        global flag_fake_vr
        flag_fake_vr = True
        user = pp_user(test_user['bidno'], test_user['passwd'], None, server_dict, machine2)
        user.client.login.do_shoot()

def test_image_vrerr():
        global flag_fake_vr
        flag_fake_vr = True
        user = pp_user(test_user['bidno'], test_user['passwd'], None, server_dict, machine2)
        user.client.bid[0].image.do_warmup()
        user.client.bid[0].image.do_shoot()

def test_price_vrerr():
        global flag_fake_vr
        flag_fake_vr = True
        user = pp_user(test_user['bidno'], test_user['passwd'], None, server_dict, machine2)
        user.client.bid[0].price.do_warmup()
        user.client.bid[0].price.do_shoot()

#----------------------------------------------------------

def pp_init_mac():
        global machine, machine2, server_dict, pp_server_dict, pp_server_dict_2, server_group
        server_dict = (pp_server_dict, pp_server_dict_2)[server_group]
        machine     = pp_machine('Enmh80vDVlPG')
        machine2    = pp_machine('C0HeVkQXFzRd1co')

#----------------------------------------------------------

#----------------------------------------------------------

func_list =     {
                'login_normal'    :     test_login_normal   ,
                'image_normal'    :     test_image_normal   ,
                'price_normal'    :     test_price_normal   ,
                'login_mac2'      :     test_login_mac2     ,
                'image_mac2'      :     test_image_mac2     ,
                'price_mac2'      :     test_price_mac2     ,
                'login_ccerr'     :     test_login_ccerr    ,
                'image_ccerr'     :     test_image_ccerr    ,
                'price_ccerr'     :     test_price_ccerr    ,
                'login_vrerr'     :     test_login_vrerr    ,
                'image_vrerr'     :     test_image_vrerr    ,
                'price_vrerr'     :     test_price_vrerr    ,
                }

def usage():
        string = ''
        cmds = sorted(func_list.keys())
        for cmd in cmds:
                string += ('./pp_test.py %s\n' % cmd)
        print(string)
                        
def pp_test(argv):
        if len(argv) != 2 :
                usage()
                return 
        if not argv[1] in func_list :
                usage()
                return 
        #pp_init_dump()
        pp_init_dns()
        pp_init_mac()
        func_list[argv[1]]()
        #pp_write_dump()

if __name__ == "__main__":
        pp_test(sys.argv)

