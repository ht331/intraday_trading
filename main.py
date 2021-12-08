

from model.version_1.make_data import *


if __name__ == '__main__':
    s = 'select trade_date from stock.tradedate where trade_date >= "2021-01-01" and trade_date <= "2021-12-08"'
    v = engine.exec_query(s)
    date_list = [i[0].strftime("%F") for i in v]

    for date in date_list:
        try:
            df = get_data(date)
            engine.update_df(df, 'it_model_data')
            print(date)
        except:
            print('no', date)