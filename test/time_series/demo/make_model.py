# -*- coding: utf-8 -*-

"""
    构建模型

    1.adf检验
    2.白噪声检验
    3.参数选择
    4.建模
    5.预测
    6.画图

created on 2021/12/10 4:36 下午
@author:huangtao
@contact:huangtao@163.com

"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import acorr_ljungbox


class IDArima:

    def __init__(self, df_train, df_test):
        self.ts = df_train
        self.test = df_test

        # self.adf_test()
        # self.ljungbox_test()
        # self.para_select()
        # self.make_model()
        # self.make_fig()

    def adf_test(self):
        result = adfuller(self.ts)
        print(result)

    def ljungbox_test(self):
        pass

    def para_select(self):
        pass

    def make_model(self):
        pass

    def model_predict(self):
        pass

    def make_fig(self):
        pass
