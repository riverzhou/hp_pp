#!/usr/bin/env python3

from pickle         import  dump, load
from traceback      import  print_exc

from pp_log         import  logger, printer


db_name = 'pp_db.dump'

class DataBase():
        pass

database = DataBase

def load_dump():
        global db_name, database
        try:
                f = open(db_name, 'rb')
                database = load(f)
                f.close()
                logger.info('DataBase loaded')
        except FileNotFoundError:
                pass
        except:
                print_exc()


def save_dump():
        global db_name, database
        try:
                f = open(db_name, 'wb', True)
                dump(database, f)
                f.close()
                logger.info('DataBase saved')
        except:
                print_exc()

