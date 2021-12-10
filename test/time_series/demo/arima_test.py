# -*- coding: utf-8 -*-

"""
        使用arima模型预测

        使用level2 数据的价格
        平滑处理 3秒 一个值

created on 2021/12/10 4:09 下午
@author:huangtao
@contact:huangtao@163.com

"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sql_conn import get_engine, LV2_REMOTE_MYSQL_PARA
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import acorr_ljungbox
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.arma_mle import Arma

import warnings
warnings.filterwarnings('ignore', 'statsmodels.tsa.arima_model.ARMA',
                        FutureWarning)
warnings.filterwarnings('ignore', 'statsmodels.tsa.arima_model.ARIMA',
                        FutureWarning)


engine = get_engine(**LV2_REMOTE_MYSQL_PARA)


def get_data():
    s = 'select time, new_price from tickstock211208 where time >= 93000000 and code = "300712"'
    v = engine.exec_query(s)
    df = pd.DataFrame(data=v, columns=['time', 'price'])

    # time_list = list(np.arange(93000000, 113000000, 3000)) + list(np.arange(130000000, 150000000, 3000))
    # df_ = pd.DataFrame()
    # df_['time'] = time_list
    # df_ = df_.merge(df, on='time', how='left')
    # df_.fillna(method='ffill', inplace=True)
    # df_.set_index('time')

    df.set_index('time', inplace=True)

    return df


def split_train_test(data, t):
    """
        将一天的tick分成
        train

        test
    :param data:
    :return:
    """
    df_train = data[data.time < t]
    df_test = data[data.time >= t]
    return df_train, df_test



df = get_engine()
df_train, df_test = split_train_test(df, 103000000)

ts = df_train

# ADF检验
result = adfuller(ts)
print(result)

# (-3.5556007557039386,
#  0.006668830131562699,
#  5,
#  1186,
#  {'1%': -3.4358757250664356,
#   '5%': -2.8639800492824805,
#   '10%': -2.568069130240666},
#  -2880.6436043691106)

# t值满足，p值满足，严格拒绝原假设


# 白噪声检验

res = acorr_ljungbox(ts, lags=[2, 3, 4, 6, 8, 9, 10], boxpierce=False)
# (array([ 2302.98044753,  3423.33174372,  4516.76055435,  6618.16322591,
#          8601.70202856,  9546.43853296, 10459.31962754]),
#  array([0., 0., 0., 0., 0., 0., 0.]))

# 拒绝原假设，ts不是白噪声

# 模型定阶
train_results = sm.tsa.arma_order_select_ic(ts, ic=['aic', 'bic'], trend='nc', max_ar=8, max_ma=8)
print('AIC', train_results.aic_min_order)  # 建立AIC最小的模型
# AIC (1, 3)
model = ARIMA(ts, order=(1, 0, 3)).fit()
model.summary()

model.conf_int()


# 残差白噪声检验
resid = model.resid  # 提取残差
# 残差白噪声检验
lag = [i+1 for i in range(30)]
res2 = acorr_ljungbox(resid**2, lags=lag, boxpierce=False)
print(res2)

# p值都大于0.05, 不是白噪声，有ARCH效应

from arch import arch_model
am = arch_model(resid)  # 默认模型是GARCH(1,1）
model2 = am.fit(update_freq=0)  # 估计参数

print(model2.summary())
