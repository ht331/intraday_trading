# -*- coding: utf-8 -*-

"""

created on 2021/12/10 10:28 上午
@author:huangtao
@contact:huangtao@163.com

"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sql_conn import get_engine, STOCK_125_MYSQL_PARA

engine = get_engine(**STOCK_125_MYSQL_PARA)

# 从minute表获取某天某只股票的数据
s = 'select local_date, local_datetime, code, price' \
    ' from stock.minute_his where local_date = "2021-12-07" and code = "300712" and price!=0'
v = engine.exec_query(s)
df = pd.DataFrame(data=v, columns=v[0]._parent.keys)
df.sort_values(by='local_datetime', inplace=True)
df.set_index('local_datetime', inplace=True)
ts = df['price']


# PART 1
# ADF单位根检验
from statsmodels.tsa.stattools import adfuller
result = adfuller(ts)
print(result)

# 判断是否决绝原假设，原序列是否存在单位根
# 若不能拒绝原假设，则存在单位根，一阶差分后再次进行ADF检验
# (-3.224645392266501,
#  0.01860170013260725,
#  12,
#  228,
#  {'1%': -3.4593607492757554,
#   '5%': -2.8743015807562924,
#   '10%': -2.5735714042782396},
#  -198.06055411670934)

# 此处ADF检验判断拒绝原假设，但不是严格拒绝，还是进行一阶差分

ts1 = ts.diff().dropna()
result = adfuller(ts1)
print(result)
# #
# (-4.05626080093635,
#  0.0011429366261408009,
#  11,
#  228,
#  {'1%': -3.4593607492757554,
#   '5%': -2.8743015807562924,
#   '10%': -2.5735714042782396},
#  -188.96828891361451)

# 此时严格拒绝原假设


# PART 2
# 白噪声检验, Ljung-Box检验
from statsmodels.stats.diagnostic import acorr_ljungbox
res = acorr_ljungbox(ts1, lags=[6, 8, 9, 10], boxpierce=False)
print(res)

# (array([ 9.98921921, 19.50774297, 21.59235897, 23.87577683]),
#  array([0.12510676, 0.01236783, 0.01026469, 0.00793703]))
# 13阶延迟后p值小于0.05 认为ts1不是一个白噪声，


# PART 3
# 模型识别与定阶
# 方法1
# ARIMA(p,d,q)模型，其中d是差分次数。

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
plot_acf(ts1, use_vlines=True, lags=30)  # 自相关函数，滞后30阶
plt.show()

plot_pacf(ts1, use_vlines=True, lags=30)  # 偏自相关函数图
plt.show()

# 判断p=1，q=1


from statsmodels.tsa.arima.model import ARIMA
model = ARIMA(ts1, order=(1, 1, 1))
result = model.fit(disp=-1)

result.summary()


# 方法2
# 模型定阶（或者使用acf， pacf图）
train_results = sm.tsa.arma_order_select_ic(ts1, ic=['aic', 'bic'], trend='nc', max_ar=8, max_ma=8)
# max_ar 限制ar的最大阶数
# max_ma 限制ma的最大阶数

print('AIC', train_results.aic_min_order)  # 建立AIC最小的模型
# AIC (4, 7)
# print('BIC', train_results.bic_min_order)

model = ARIMA(ts, (4, 1, 7)).fit()
model.summary()  # 提取模型系数等信息，保留三位小数，


# PART 3
# 模型诊断

model.conf_int()

import math
stdresid = model.resid/math.sqrt(model.sigma2)  # 标准化残差
# plt.rcParams['font.sans-serif'] = ['simhei']  #字体为黑体
plt.rcParams['axes.unicode_minus'] = False  #正常显示负号
plt.plot(stdresid) #标准化残差序列图
plt.xticks(rotation=45) #坐标角度旋转
plt.xlabel('日期') #横、纵坐标以及标题命名
plt.ylabel('标准化残差')
plt.title('标准化残差序列图',loc='center')

# 对残差进行白噪声检验
# from statsmodels.stats.diagnostic import acorr_ljungbox
lag = [i+1 for i in range(30)]
res1 = acorr_ljungbox(stdresid, lags=lag, boxpierce=False)
print(res1)

# 绝大部分p值大于0.05， 接受原假设， 残差是白噪声


# PART 5 模型预测

a = model.forecast(2)

# fig, ax = plt.subplots(figsize=(6, 4))
# ax = ts.ix['2018-09':].plot(ax=ax)
# plt.show()


fig = model.plot_predict(5, 280)


# ARCH 模型

resid1 = model.resid  # 提取残差
# 残差白噪声检验

lag = [i+1 for i in range(30)]
res2 = acorr_ljungbox(resid1**2, lags=lag, boxpierce=False)
print(res2)
# p值都小于0.05 接受原假设，则残差序列没有ARCH效应


# 若p值大于0.05 ，则残差序列有ARCH效应
# from arch imort arch_model
# am = arch_model(resid1)  # 默认模型是GARCH(1,1）
# model2 = am.fit(update_freq=0)  # 估计参数
#
# print(model2.summary())