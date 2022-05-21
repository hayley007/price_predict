#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glassnode import GlassnodeClient
# from time import time
import time

import numpy as np
import pandas as pd
from tqdm import tqdm
import datetime
import json

def get_indicator_data(start_time,end_time):

    gn = GlassnodeClient()
    api_key = '27B7d366MLdyKjAIP15Og5BncOj'
    gn.set_api_key(api_key)

    df = pd.DataFrame()

    filename = './glassnode_indicator.xlsx'
    read_excel_file = pd.read_excel(filename)
    keys = read_excel_file.keys()
    for en,cn ,api_url,exchange,coin_type in tqdm(zip(read_excel_file[keys[0]],read_excel_file[keys[1]],
                                            read_excel_file[keys[2]],read_excel_file[keys[3]],
                                            read_excel_file[keys[4]])):

        print('en: ', en, 'cn: ',cn)
        indicator = '-'.join(en.split(' ') )
        data = pd.DataFrame()

        if pd.isnull(coin_type):
            coin_type = 'BTC'

        if pd.isnull(exchange):
            # print('NAN!!!')
            data = gn.get(
                api_url,
                a=coin_type,
                s=start_time,
                u=end_time,
                i='24h'
            )
        else:
            print('exchange: ', exchange)
            data = gn.get(
                api_url,
                a=coin_type,
                s=start_time,
                u=end_time,
                i='24h',
                e = exchange
            )

        # print(data)
        if indicator == 'Spent-Output-Age-Bands' or indicator == 'Options-ATM-Implied-Volatility-(All)':
            df_sub = pd.json_normalize(data).set_index(data.index)
            # print(df_sub.head(5))
            df = pd.concat([df, df_sub], axis=1)
            continue

        if indicator == 'URPD':
            # data = data.drop(['partitions'],axis=1) #删除列
            # print(data)
            current_supply_list = []

            for i,row in data.iterrows():
                partitions_list = row['partitions']
                ath_price_ori = row['ath_price']
                ath_price = float(ath_price_ori)
                current_price_ori = row['current_price']
                total_supply_ori = row['total_supply']
                current_price = float(current_price_ori)

                price_list = []
                for i in range(0, 100):
                    price = i * ath_price / 100
                    price_list.append(price)

                price_list_show = []
                partitions_list_show = []
                position = 0
                for i in range(1, 100, 2):
                    price_list_show.append(price_list[i])
                    partitions_list_show.append(partitions_list[i])

                # print('price_list_show: ',len(price_list_show) )
                for i in range(0, 49):
                    if current_price >= price_list_show[i] and current_price <= price_list_show[i + 1]:
                        position = i
                        break
                if current_price == ath_price:
                    position = 49
                current_supply = partitions_list_show[position]
                current_supply_list.append(current_supply)
                # print('current_supply:', current_supply)

            t = data.reset_index()['t']
            df_sub = pd.DataFrame(list(zip(t, current_supply_list)),columns=['t','current_supply'])
            df_sub = df_sub.set_index('t')
            # print(df_sub)
            df = pd.concat([df, df_sub], axis=1)
            continue

        data.rename(indicator, inplace=True)
        # print(type(data))
        df = pd.concat([df, data], axis=1)
        print(df.head(5))

        time.sleep(1)

    # print(df.columns )
    return df

# df = get_indicator_data()






