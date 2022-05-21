#!/usr/bin/env python

import os
from time import time
import numpy as np
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import random
import json
from get_glassnode_data import *

from tensorflow.python.keras.preprocessing import sequence
from tensorflow.python.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler,StandardScaler


def createXY(dataset,n_past):
    dataX = []

    for i in range(n_past, len(dataset)):
            dataX.append(dataset[i - n_past:i, :dataset.shape[1]])

    return np.array(dataX)

if __name__ == '__main__':

    model = load_model('./glass_reg.h5')
    print('model load success...')

    featrue_set = ['Price', 'Mt-Gox-Balance', 'Accumulation-Balance', 'Binance-Inflow-Volume', 'UTXOs-Spent',
                   'Exchange-Balance',
                   'Binance-Outflow-Volume-', 'Futures-Long-Liquidations-(Total)', 'Wrapped-BTC-(WBTC)-Balance',
                   'Addresses-with-Balance-10', 'Highly-Liquid-Supply', 'Supply-Held-by-Entities-with-Balance-100---1k',
                   'Sending-Addresses', 'New-Addresses-', 'Supply-Held-by-Entities-with-Balance-10k---100k',
                   'Addresses-with-Balance-01', 'Transfer-Volume-in-Profit', 'UTXOs', 'asol', 'Accumulation-Addresses',
                   'Spent-Volume-6m-12m', 'Number-of-Whales', 'Exchange-Outflow-Volume', 'Mempool-Transaction-Count',
                   'Addresses-with-Balance-100', 'Spent-Volume-1w-1m', 'Short-Term-Holder-Supply-in-Loss',
                   'UTXOs-in-Loss',
                   'Liquid-Supply', 'Options-Volume', 'Receiving-Addresses', 'Futures-Volume', '1m', '1w', '3m', '6m',
                   'Coin-Days-Destroyed', 'Futures-Perpetual-Funding-rate', 'Lightning-Network-Channel-Size-(Mean)',
                   'Transfer-Volume-(Total)', 'US-Month-over-Month-Price-Change', '1d_1w', '1h', '1h_24h', '1m_3m',
                   '1w_1m', '1y_2y',
                   '2y_3y', '3m_6m', '3y_5y', '5y_7y', '6m_12m', '7y_10y', 'more_10y', 'STH-SOPR',
                   'Luna-Foundation-Guard-Balance',
                   'Spent-Volume-3m-6m', 'Exchange-Inflow-Volume', 'Hodler-net-position', 'USDT-Balance',
                   'Transfer-Volume-in-Loss',
                   'Herfindahl-Index', 'Addresses-with-Balance-1', 'Total-Addresses', 'Coinbase-Inflow-Volume',
                   'Miner-Unspent-Supply', 'Gini-Coefficient', 'Coinbase-Outflow-Volume-',
                   'Long-Term-Holder-Supply-in-Loss',
                   'Options-Open-Interest', 'Spent-Volume-3y-5y', 'Supply-Held-by-Entities-with-Balance-100k',
                   'EU-Month-over-Month-Price-Change', 'Futures-Short-Liquidations-(Total)', 'NVT-Signal',
                   'Lightning-Network-Number-of-Nodes', 'Realized-Profit', 'Miner-Net-Position-Change',
                   'Addresses-with-Balance-10k',
                   'Futures-Long-Liquidations-Dominance', 'Futures-Open-Interest', 'Withdrawing-Addresses',
                   'Supply-Held-by-Entities-with-Balance-1k---10k', 'Spent-Volume-1m-3m', 'LTH-SOPR',
                   'Lightning-Network-Capacity',
                   'BUSD-Balance', 'Liquid-Supply-Change', 'Percent-UTXOs-in-Profit', 'UTXOs-in-Profit', 'USDC-Balance',
                   'CVDD',
                   'Addresses-with-Balance-1k', 'NVT-Ratio-', 'Illiquid-Supply-Change', 'Active-Addresses',
                   'Depositing-Addresses',
                   'current_supply', 'Futures-Estimated-Leverage-Ratio', 'Percent-Addresses-in-Profit', 'Miner-Balance',
                   'Asia-Month-over-Month-Price-Change', 'Addresses-with-Non-Zero-Balance', 'Short-Term-Holder-Supply']

    predict_file = 'predict.xlsx'

    start_time = (datetime.datetime.now() - datetime.timedelta(days=13)).strftime("%Y-%m-%d")
    current_time = (datetime.datetime.now()).strftime("%Y-%m-%d")
    end_time = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")


    if os.path.exists(predict_file):
        df = pd.read_excel(predict_file)
    else:
        df = get_indicator_data(start_time,end_time)
        df.to_excel(predict_file)

    keys = df.keys().to_list()

    df_filter = df.loc[:, featrue_set]
    input_data = df_filter.tail(4).values

    sc = MinMaxScaler(feature_range=(0, 1))
    test_set_scaled = sc.fit_transform(input_data)

    n_step = 3
    test_X = createXY(test_set_scaled, n_step)
    

    yhat = model.predict(test_X)
    prediction_copies_array = np.repeat(yhat, test_X.shape[2], axis=-1)
    inv_yhat = sc.inverse_transform(np.reshape(prediction_copies_array, (len(yhat), test_X.shape[2])))[:, 0]
    print('predict: ',inv_yhat)
    print('predict today: ', inv_yhat[-1])

    df_7_days_past = df.head(7)
    df_7_days_future = df.iloc[7:,:]
    df_7_days_future["Price"] = df_7_days_future["Price"].map(lambda x: x*0)

    df_7_days_future = df_7_days_future[featrue_set]
    old_scaled_array = sc.transform(df_filter.head(7))
    new_scaled_array = sc.transform(df_filter.tail(7))
    new_scaled_df = pd.DataFrame(new_scaled_array)
    new_scaled_df.iloc[:, 0] = np.nan
    full_df = pd.concat([pd.DataFrame(old_scaled_array), new_scaled_df]).reset_index().drop(["index"], axis=1)

    full_df_scaled_array = full_df.values
    all_data = []
    time_step = 7
    for i in range(time_step, len(full_df_scaled_array)):
        data_x = []
        data_x.append(
            full_df_scaled_array[i - n_step:i, :full_df_scaled_array.shape[1]])
        data_x = np.array(data_x)

        prediction = model.predict(data_x)
        all_data.append(prediction)
        full_df.iloc[i, 0] = prediction

    new_array = np.array(all_data)
    new_array = new_array.reshape(-1, 1)
    prediction_copies_array = np.repeat(new_array, test_X.shape[2], axis=-1)
    y_pred_future_7_days = sc.inverse_transform(np.reshape(prediction_copies_array, (len(new_array), test_X.shape[2])))[:, 0]
    print('future_7_days: ',y_pred_future_7_days)



