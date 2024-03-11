#coding=utf-8
from databases import Database


__all__ = ['db']

# 数据库实例
import setting

db: Database = Database(
    f'mysql+pymysql://{setting.MYSQL_USER}:{setting.MYSQL_PWD}@{setting.MYSQL_HOST}:{setting.MYSQL_POST}/{setting.MYSQL_DB_NAME}?charset=utf8mb4',
    min_size=5,    # 数据库连接池最小值
    max_size=20,    # 数据库连接池最大值
    pool_recycle=300)    # 数据库连接最大空闲时间

