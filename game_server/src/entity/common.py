#coding=utf-8
from dataclasses import fields
from sqlalchemy.dialects import mysql

from .base import Base, ModelBase
from sqlalchemy import Column, String, text

class GameQuarry(Base):
	__tablename__ = 'game_quarry'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8mb4',
		'mysql_collate': 'utf8mb4_general_ci',
		'mysql_row_format': 'Dynamic',
		'mysql_auto_increment': '1',
		'comment': '矿石表',
	}
	id = Column(mysql.BIGINT(10, unsigned=True), primary_key=True, comment='主键')
	user_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="用户id")
	current_number = Column(mysql.DECIMAL(50, 20, unsigned=True), nullable=True, server_default=text("0"), comment="当前采集量")
	total_number = Column(mysql.DECIMAL(50, 20, unsigned=True), nullable=True, server_default=text("0"), comment="累计采集量")




class User(Base,ModelBase):
	__tablename__ = 'users'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8mb4',
		'mysql_collate': 'utf8mb4_general_ci',
		'mysql_row_format': 'Dynamic',
		'mysql_auto_increment': '1',
		'comment': '用户表',
	}
	
	user_name = Column(String(100), nullable=False, server_default='', comment='用户名')
	pwd = Column(String(100), nullable=False, server_default='', comment='密码')


	glod_coin = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="金币")
	sliver_coin = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="银币")
	fight = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="战力")
	grade = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="等级")
	phy = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="体力")
	exp = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="经验")
	icon = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="头像")
	last_sign_day = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="最后签到的时间，距离月初")
	sign_count = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="登录领奖次数")
	last_lottery_day = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="最后抽奖时间，距离特定时间")
	shop_data = Column(String(100), nullable=False, server_default='', comment='商城数据')
	level = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="关卡")
	is_first_day_login = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="今天第一次登录")
	is_first_month_login = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"),
	                            comment="本月第一次登录")
	task_data = Column(String(100), nullable=False, server_default='', comment='任务数据')
	guide = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="指引")
	
class Hero(Base, ModelBase):
	__tablename__ = 'hero'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8mb4',
		'mysql_collate': 'utf8mb4_general_ci',
		'mysql_row_format': 'Dynamic',
		'mysql_auto_increment': '1',
		'comment': '英雄表',
	}


	user_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="用户id")
	hero_num = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="英雄编号")
	hero_grade = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="等级")
	hero_fight = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="战力")
	hero_exp = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="经验")


class HeroRune(Base):
	__tablename__ = 'hero_rune'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8mb4',
		'mysql_collate': 'utf8mb4_general_ci',
		'mysql_row_format': 'Dynamic',
		'mysql_auto_increment': '1',
		'comment': '英雄装备',
	}
	
	id = Column(mysql.BIGINT(10, unsigned=True), primary_key=True, comment='主键')
	hero_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="英雄id")
	user_rune_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="用户符文信息")
	rune_num = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="符文编号")
	rune_pos = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="装备位置")


class UserRune(Base):
	__tablename__ = 'user_rune'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8mb4',
		'mysql_collate': 'utf8mb4_general_ci',
		'mysql_row_format': 'Dynamic',
		'mysql_auto_increment': '1',
		'comment': '用户符文',
	}
	
	id = Column(mysql.BIGINT(10, unsigned=True), primary_key=True, comment='主键')
	user_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="用户id")
	rune_num = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="符文编号")
	is_put = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="是否装备")


class UserItem(Base):
	__tablename__ = 'user_item'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8mb4',
		'mysql_collate': 'utf8mb4_general_ci',
		'mysql_row_format': 'Dynamic',
		'mysql_auto_increment': '1',
		'comment': '用户物品',
	}
	
	id = Column(mysql.BIGINT(10, unsigned=True), primary_key=True, comment='主键')
	user_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="用户id")
	item_num = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="物品编号")
	item_amount = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="物品数量")

class UserEmail(Base, ModelBase):
	__tablename__ = 'user_email'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8mb4',
		'mysql_collate': 'utf8mb4_general_ci',
		'mysql_row_format': 'Dynamic',
		'mysql_auto_increment': '1',
		'comment': '用户邮件',
	}


	user_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="用户id")
	item_json = Column(String(100), nullable=False, server_default='', comment='奖励物品')
	email_title = Column(String(100), nullable=False, server_default='', comment='邮件标题')
	email_content = Column(String(100), nullable=False, server_default='', comment='邮件内容')
	is_read = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="是否已读")
	is_get = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="是否领取")


class HeroTeam(Base):
	__tablename__ = 'hero_team'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8mb4',
		'mysql_collate': 'utf8mb4_general_ci',
		'mysql_row_format': 'Dynamic',
		'mysql_auto_increment': '1',
		'comment': '英雄布阵',
	}
	
	id = Column(mysql.BIGINT(10, unsigned=True), primary_key=True, comment='主键')
	hero_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="英雄ID")
	team_pos = Column(mysql.INTEGER(10, unsigned=True), nullable=False, server_default=text("0"), comment="队伍位置")
	user_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="用户id")


class UserFriend(Base):
	__tablename__ = 'user_friend'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8mb4',
		'mysql_collate': 'utf8mb4_general_ci',
		'mysql_row_format': 'Dynamic',
		'mysql_auto_increment': '1',
		'comment': '用户好友',
	}
	
	id = Column(mysql.BIGINT(10, unsigned=True), primary_key=True, comment='主键')
	user_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="用户id")
	friend_user_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="好友用户id")


class UserFriendReq(Base, ModelBase):
	__tablename__ = 'user_friend_req'
	__table_args__ = {
		'mysql_engine': 'InnoDB',
		'mysql_charset': 'utf8mb4',
		'mysql_collate': 'utf8mb4_general_ci',
		'mysql_row_format': 'Dynamic',
		'mysql_auto_increment': '1',
		'comment': '用户好友请求表',
	}
	
	id = Column(mysql.BIGINT(10, unsigned=True), primary_key=True, comment='主键')
	req_user_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="发送请求用户id")
	friend_user_id = Column(mysql.BIGINT(10, unsigned=True), nullable=False, server_default=text("0"), comment="好友用户id")


