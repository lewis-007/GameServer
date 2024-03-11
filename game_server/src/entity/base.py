# coding=utf-8
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, text, String, DateTime

# 数据库模型基类

from utils import datetime_util

Base = declarative_base()


class ModelBase():
	id = Column(mysql.BIGINT(10, unsigned=True), primary_key=True, comment='主键')
	is_delete = Column(mysql.TINYINT(1, unsigned=True), nullable=False, server_default=text('0'), comment='是否删除: [0=否, 1=是]')
	create_time = Column(DateTime(), nullable=False, default=datetime_util.get_now_str(), comment='创建时间')
	update_time = Column(DateTime(), nullable=False, default=datetime_util.get_now_str(), comment='更新时间')
	delete_time = Column(DateTime(), nullable=False, default=datetime_util.get_now_str(), comment='删除时间')
	remarks = Column(String(200), nullable=True, server_default='', comment='备注信息')
