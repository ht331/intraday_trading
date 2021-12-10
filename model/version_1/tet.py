# -*- coding: utf-8 -*-

"""
 对 000001 进行建模

created on 2021/12/9 2:43 下午
@author:huangtao
@contact:huangtao@163.com

"""

from sql_conn import get_engine, STOCK_125_MYSQL_PARA
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn import metrics

engine = get_engine(**STOCK_125_MYSQL_PARA)


def get_data():
    s = 'select * from Test.it_model_data where local_date <= "2021-10-01"'
    v = engine.exec_query(s)
    df = pd.DataFrame(data=v, columns=v[0]._parent.keys)
    return df


data = get_data()
data.dropna(inplace=True)
xcol = [str(i) for i in range(60)]

X = data[xcol]
y = data['amp']
# y = data['label']

x_train, x_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=10)

reg = GradientBoostingRegressor()
reg.fit(x_train, y_train)
y_pred = reg.predict(x_test)

print(metrics.r2_score(y_pred=y_pred, y_true=y_test))


clf = GradientBoostingClassifier()
clf.fit(x_train, y_train)
y_pred = clf.predict(x_test)

print(metrics.classification_report(y_pred=y_pred, y_true=y_test))
