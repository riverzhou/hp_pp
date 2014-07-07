#!/usr/bin/env python3

from pp_udpworker   import udp_worker

from pp_log         import logger
from pp_config      import pp_config

#=============================================================

def main():
        global pp_config

        arg_val =({},{})
        udp =[None,None]

        arg_val[0]['bidno'] = pp_config['udp_bidno']
        arg_val[0]['pid']   = pp_config['udp_pid']
        arg_val[0]['group'] = 0
        arg_val[1]['bidno'] = pp_config['udp_bidno']
        arg_val[1]['pid']   = pp_config['udp_pid']
        arg_val[1]['group'] = 1

        udp[0] = udp_worker(None, arg_val[0])
        udp[1] = udp_worker(None, arg_val[1])

        udp[0].start()
        udp[1].start()

        udp[0].wait_for_start()
        udp[1].wait_for_start()

        logger.debug('UDP threads init finished.')

        udp[0].join()
        udp[1].join()

if __name__ == '__main__' :
        try:
                main()
        except KeyboardInterrupt:
                pass
        except:
                print_exc()
        finally:
                print()

