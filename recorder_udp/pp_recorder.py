#!/usr/bin/env python3

from pp_udpworker   import fd_udp_init, daemon_udp

from pp_log         import logger
from pp_config      import pp_config

from pp_server      import pp_dns_init


#=============================================================

def main():
        global pp_config, daemon_udp

        pp_dns_init()
        fd_udp_init()

        account = (pp_config['udp_bidno'], pp_config['udp_pid'])

        daemon_udp.add(account)
        daemon_udp.add(account)

        logger.debug('UDP threads init finished.')

        daemon_udp.wait_for_stop()

if __name__ == '__main__' :
        try:
                main()
        except  KeyboardInterrupt:
                pass
        except:
                print_exc()
        finally:
                print()

