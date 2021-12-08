"""
    level-1的数据，只考虑量价 percentage， volume

    使用分钟数据, 每30分钟作为一个输入，预测30分钟后的涨幅

    240 / 30 = 8
    x:
    pi (i = 1,...,30) pct
    vi (i = 1,...,30) volume / ltgb

    y:
    p


    level2的数据可以考虑委托， bid，ask，bid cancel，ask cancel，

    （
    大委托买单，
    大委托卖单
    大额撤买单，
    大额撤卖单

    委托单的行为以后再分析，先对成交单进行处理：

    大额成交买单，
    大额成交卖单

    在每分钟区间内的：总量，总金额，总笔数，
"""


from sql_conn import get_engine, STOCK_125_MYSQL_PARA
import pandas as pd
import numpy as np


engine = get_engine(**STOCK_125_MYSQL_PARA)
trade_time = [i.strftime("%H:%M:%S") for i in pd.date_range('09:30:00', '11:30:00', freq='1min').to_list() +
              pd.date_range('13:01:00', '15:00:00', freq='1min').to_list()]
time_list = [i.strftime("%H:%M:%S") for i in pd.date_range('09:30:00', '11:30:00', freq='30min').to_list() +
              pd.date_range('13:30:00', '15:00:00', freq='30min').to_list()]


def get_data(date):

    s = 'select local_datetime, code, percent, volume, amount' \
        ' from stock.minute%s where local_date = "%s" and local_datetime >= "%s 09:25:00"'
    ss = s % ('', date, date)
    v = engine.exec_query(ss)
    if len(v) == 0:
        ss = s % ('_his', date, date)
        v = engine.exec_query(ss)

    data = pd.DataFrame(data=v, columns=v[0]._parent.keys)
    data['local_datetime'] = data[['local_datetime']].astype(str)
    data[['local_date', 'local_time']] = data['local_datetime'].str.split(' ', expand=True)
    code_ = list(set(data[data.amount >= 200000000].code.to_list()))  # 当天成交额要大于2个亿
    data = data[data.code.isin(code_)]

    def group_code(df):
        df__ = pd.DataFrame()
        df__['local_time'] = trade_time
        df_ = df.copy()
        df_.drop_duplicates(subset=['local_time'], inplace=True)
        df_.sort_values(by='local_time', inplace=True)
        df_.reset_index(drop=True, inplace=True)
        v_ = [0] + df_.volume.to_list()[:-1]
        a_ = [0] + df_.amount.to_list()[:-1]

        df_['v_'] = v_
        df_['a_'] = a_

        df_['vol'] = df_.volume - df_.v_
        init_v = df_.vol[df_.vol != 0].values[0]
        df_['vol_r'] = df_.vol / init_v
        df_['amt'] = df_.amount - df_.a_

        df__ = df__.merge(df_, on='local_time', how='left')
        df__.fillna(method='ffill', inplace=True)
        df__.drop_duplicates(inplace=True)

        df___ = pd.DataFrame()
        for j in range(len(time_list) - 2):
            start_time = time_list[j]
            end_time = time_list[j + 1]
            pred_time = time_list[j + 2]
            tmp_df = df__[(df__.local_time >= start_time) & (df__.local_time < end_time)]
            x = np.array(tmp_df[['percent', 'vol_r']])
            y = x.T.ravel()
            ydf = pd.DataFrame(data=y.reshape(1, 60), index=[j])
            p1 = df__.percent[df__.local_time == pred_time].values[0]
            p0 = df__.percent[df__.local_time == end_time].values[0]
            amp = p1 - p0
            label = 1 if amp > 0 else 0
            ydf['pct'] = p1
            ydf['amp'] = amp
            ydf['label'] = label
            df___ = df___.append(ydf, sort=False)
        # df___.reset_index(inplace=True)

        return df___

    r_df = data.groupby('code').apply(group_code)
    r_df.reset_index(inplace=True)
    r_df['local_date'] = date
    return r_df





