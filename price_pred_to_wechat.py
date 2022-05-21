

from AlarmBot import alarmBot
import time
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




class LSTM_Reg_Predict(object):

    def __init__(self):
        self.model = load_model('./glass_reg.h5')
        print('model load success...')

        self.featrue_set = ['Price', 'Mt-Gox-Balance', 'Accumulation-Balance', 'Binance-Inflow-Volume', 'UTXOs-Spent',
                       'Exchange-Balance',
                       'Binance-Outflow-Volume-', 'Futures-Long-Liquidations-(Total)', 'Wrapped-BTC-(WBTC)-Balance',
                       'Addresses-with-Balance-10', 'Highly-Liquid-Supply',
                       'Supply-Held-by-Entities-with-Balance-100---1k',
                       'Sending-Addresses', 'New-Addresses-', 'Supply-Held-by-Entities-with-Balance-10k---100k',
                       'Addresses-with-Balance-01', 'Transfer-Volume-in-Profit', 'UTXOs', 'asol',
                       'Accumulation-Addresses',
                       'Spent-Volume-6m-12m', 'Number-of-Whales', 'Exchange-Outflow-Volume',
                       'Mempool-Transaction-Count',
                       'Addresses-with-Balance-100', 'Spent-Volume-1w-1m', 'Short-Term-Holder-Supply-in-Loss',
                       'UTXOs-in-Loss',
                       'Liquid-Supply', 'Options-Volume', 'Receiving-Addresses', 'Futures-Volume', '1m', '1w', '3m',
                       '6m',
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
                       'BUSD-Balance', 'Liquid-Supply-Change', 'Percent-UTXOs-in-Profit', 'UTXOs-in-Profit',
                       'USDC-Balance',
                       'CVDD',
                       'Addresses-with-Balance-1k', 'NVT-Ratio-', 'Illiquid-Supply-Change', 'Active-Addresses',
                       'Depositing-Addresses',
                       'current_supply', 'Futures-Estimated-Leverage-Ratio', 'Percent-Addresses-in-Profit',
                       'Miner-Balance',
                       'Asia-Month-over-Month-Price-Change', 'Addresses-with-Non-Zero-Balance',
                       'Short-Term-Holder-Supply']

        self.predict_file = 'predict.xlsx'

        self.start_time = (datetime.datetime.now() - datetime.timedelta(days=13)).strftime("%Y-%m-%d")
        self.current_time = (datetime.datetime.now()).strftime("%Y-%m-%d")
        self.end_time = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    def createXY(self,dataset, n_past):
        dataX = []

        for i in range(n_past, len(dataset)):
            dataX.append(dataset[i - n_past:i, :dataset.shape[1]])

        return np.array(dataX)

    def _normalMsg(self, val):
        return "预测今日币价 " + str(round(val , 2))

    def getHeader(self,strong=0):
        utcNow = datetime.datetime.now(datetime.timezone.utc)
        asiatime = utcNow + datetime.timedelta(hours=8)
        ts = asiatime.strftime('%Y-%m-%d %H:%M')
        if strong == 1:
            return '*指标预警 - 强预警* \r\n [时间]：\r\n' + ts + ' (UTC+8)\r\n [数据]：\r\n'
        else:
            return '[时间]：\r\n' + ts + ' (UTC+8)\r\n [数据]：\r\n'

    def getAlert(self):

        if os.path.exists(self.predict_file):
            df = pd.read_excel(self.predict_file)
        else:
            df = get_indicator_data(self.start_time, self.end_time)
            df.to_excel(self.predict_file)

        keys = df.keys().to_list()

        df_filter = df.loc[:, self.featrue_set]
        input_data = df_filter.tail(4).values

        sc = MinMaxScaler(feature_range=(0, 1))
        test_set_scaled = sc.fit_transform(input_data)

        n_step = 3
        test_X = self.createXY(test_set_scaled, n_step)

        yhat = self.model.predict(test_X)
        prediction_copies_array = np.repeat(yhat, test_X.shape[2], axis=-1)
        inv_yhat = sc.inverse_transform(np.reshape(prediction_copies_array, (len(yhat), test_X.shape[2])))[:, 0]


        predict_price = inv_yhat[-1]
        print('predict today: ', predict_price)

        txt = self.getHeader() + self._normalMsg(predict_price)
        print('txt: ',txt)
        # bot = alarmBot('text', txt)
        # bot.post()


predict_obj = LSTM_Reg_Predict()

predict_obj.getAlert()
