#!/usr/bin/env python3




def calc_rate(list_data):
        list_rate = []
        last_number = 0
        for data in list_data:
                sn, datetime, number, count = data
                rate = number - last_number
                last_number = number
                list_rate.append((sn, datetime,rate))
        return list_rate

def calc_rate_ma(list_data, ma=5):
        list_rate = []
        list_number = []
        last_number = 0

        for data in list_data[0:ma]:
                sn, datetime, number, count = data
                rate = number - last_number
                last_number = number
                list_number.append(rate)
                list_rate.append((sn, datetime, None))

        for data in list_data[ma:]:
                sn, datetime, number, count = data
                rate = number - last_number
                last_number = number
                ma_rate = sum(list_number)/len(list_number)
                #print(rate, ma_rate)
                del (list_number[0])
                list_number.append(rate)
                list_rate.append((sn, datetime, ma_rate))

        return list_rate

