# -*- coding: utf-8 -*-

"""
mysql connection

@author: tao huang
@contact: taohuang@lengshuiriver.com
"""

from pandas.io.sql import to_sql
from pandas import read_sql_query
from sqlalchemy import create_engine
import pymysql

SQL_ERROR_MSG = 'please check mysql parameter'
pymysql.install_as_MySQLdb()


class MysqlConn:
    """
    自定义的mysql连接类， 用sqlalchemy 的engine
    """
    def __init__(self, *db):
        """
        MysqlConn 的main 函数 ，输入一串字符数据
        :param db:
        """
        self.host = db[0]
        self.port = db[1]
        self.pwd = db[2]
        self.user = db[3]
        self.db = db[4]
        self._get_engine()

    def _get_engine(self):
        """
        创建连接
        :return:
        """

        engine_url = 'mysql+mysqldb://' + self.user + ':' + self.pwd + \
                     '@' + self.host + ':' + self.port + '/' + self.db + '?charset=utf8'
        try:
            self.engine = create_engine(engine_url, pool_size=20,
                                        pool_pre_ping=True, pool_recycle=10)
        #  连接池大小5，当获取mysql连接失败时，自动刷新
        #  自动更新时间60秒
        except TypeError:
            self.engine = create_engine(engine_url)

    def exec_query(self, sql):
        """
        执行select 等有返回值的sql语句
        :param sql:
        :return: 查到的数据 list类型
        """
        conn = self.engine.connect()
        value = conn.execute(sql).fetchall()
        conn.close()
        return value

    def exec_no_query(self, sql):
        """
        执行不需要返回值的sql语句， 并直接commit
        :param sql:
        :return:
        """
        conn = self.engine.connect()
        conn.execute(sql)
        conn.close()

    def update_df(self, df, table_name):
        """
        插入一张dataframe 类型的数据表
        :param df: dataframe
        :param table_name: 插入到数据库中的表名
        :return:
        """
        to_sql(df, table_name, self.engine, index=False, schema=self.db, if_exists='append')

    def select_2_df(self, query):
        """
        配合pd ，将读取到的数据转为dataframe类型
        :param query:
        :return:
        """
        read_sql_query(self, query)

    def _pool_size(self):
        """
        取得连接池中连接的个数
        :return:
        """
        return self.engine.pool.size()

    def update_replace_df(self, df, table_name):
        """
        执行上传dataframe表至数据库，如果数据表存在数据，则替换
        :param df:
        :param table_name:
        :return:
        """
        to_sql(df, table_name, self.engine, index=False, schema=self.db, if_exists='replace')


def get_engine(**sql_para):
    """

    :param sql_para:
    :return:
    """
    host = sql_para['host']
    port = sql_para['port']
    pwd = sql_para['pwd']
    user = sql_para['user']
    db = sql_para['db']
    engine = MysqlConn(host, port, pwd, user, db)
    try:
        _check_conn(engine, db)
    except Exception:
        raise ValueError(SQL_ERROR_MSG)
    return engine


def _check_conn(engine, db):
    """
    测试是否成功连接
    :param engine:
    :param db:
    :return:
    """

    query = u'use %s;' % db
    engine.exec_no_query(query)


# STOCK_ENGINE = get_engine(**STOCK_MYSQL_PARA)
