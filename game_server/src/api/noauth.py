# coding=utf-8
from fastapi import APIRouter
import misc
from base.base import AppException
from base.http_base import HttpResp, unified_resp
from common import defines
from data import EmailData, ShopData, TaskData, GameSettingData
from entity.common import User, Hero, HeroTeam
from server_module import misc_logic
from server_module.handler_module.handler_user import HandleUser
from server_module.logic.logic_hero import LogicHero
from server_module.logic.logic_user import LogicUser
from sql import sqlplus
from sql.database import db
from utils import auth_util

router = APIRouter(prefix='/noauth')


@router.post('/register')
@unified_resp
@db.transaction()
async def register(data: dict):
	user_name = data.get("user_name")
	pwd = data.get("pwd")
	pwd2 = data.get("pwd2")
	
	if misc.is_empty(user_name):
		raise AppException(HttpResp.FAILED, msg='用户名不能为空!')
	
	if misc.is_empty(pwd):
		raise AppException(HttpResp.FAILED, msg='密码不能为空!')
	
	if pwd != pwd2:
		raise AppException(HttpResp.FAILED, msg='密码不一致!')
	
	dUser = await sqlplus.getOne(User, [User.user_name == user_name, ])
	if dUser is not None:
		raise AppException(HttpResp.FAILED, msg='用户已存在!')
	data["pwd"] = auth_util.md5(pwd)
	await sqlplus.insert(User, data)
	user_id = data["id"]
	
	hero_list = []
	for i in range(3):
		hero_list.append({
			"user_id": user_id,
			"hero_num": i,
			"hero_grade": 1,
			"hero_fight": 0,
			"hero_exp": 0,
		})
	await sqlplus.insert_list(Hero, hero_list)  # 插入英雄
	
	hero_team_lst = []
	for i in range(len(hero_list)):
		hero_id = hero_list[i]["id"]
		hero_team_lst.append({
			"hero_id": hero_id,
			"team_pos": i,
			"user_id": user_id,
		})
	
	await misc_logic.add_item(user_id, 1, 5)#增加药水
	await sqlplus.insert_list(HeroTeam, hero_team_lst, is_normal=False)  # 插入队伍
	for i in range(len(hero_list)):
		hero_id = hero_list[i]["id"]
		await LogicHero.getObj().save_hero_fight(hero_id)
	fight = await LogicUser.getObj().cal_user_fight(user_id)
	
	await sqlplus.update(User, {
		"fight": fight,
		"sliver_coin": 10000
	}, [User.id == user_id, ])
	
	return True


@router.post('/login')
@unified_resp
@db.transaction()
async def login(data: dict):
	user_name = data["user_name"]
	pwd = data["pwd"]
	
	if misc.is_empty(user_name):
		raise AppException(HttpResp.FAILED, msg='用户名不能为空!')
	
	if misc.is_empty(pwd):
		raise AppException(HttpResp.FAILED, msg='密码不能为空!')
	
	dUser = await sqlplus.getOne(User, [User.user_name == user_name, ])
	
	if dUser is None:
		raise AppException(HttpResp.FAILED, msg='用户不存在!')
	if dUser["pwd"] != auth_util.md5(pwd):
		raise AppException(HttpResp.FAILED, msg='密码错误')
	user_id = dUser["id"]
	email_data = EmailData.data.get(defines.EMAIL_LOGIN)
	is_first_day_login = dUser["is_first_day_login"]
	is_first_month_login = dUser["is_first_month_login"]
	if is_first_day_login == defines.FLAG_YES:
		# 添加邮件
		await HandleUser.getObj().add_email(user_id, {
			"user_id": user_id,
			"item_json": email_data["itemJson"],
			"email_title": email_data["title"],
			"email_content": email_data["content"],
			"is_read": 0,
			"is_get": 0
		})
		
		# 刷新商城
		shop_data_len = len(ShopData.data)
		shop_data = ""
		for i in range(shop_data_len):
			shop_data += "0"
		dUser["shop_data"] = shop_data
		
		# 刷新体力
		data = GameSettingData.data.get(0)
		dUser["phy"] = data["phyMax"]
		dUser["is_first_day_login"] = defines.FLAG_NO
	
	if is_first_month_login == defines.FLAG_YES:
		# 刷新签到
		dUser["last_sign_day"] = 0
		dUser["sign_count"] = 0
		
		dUser["is_first_month_login"] = defines.FLAG_NO
	
	await sqlplus.update(User, dUser, [User.id == user_id, ])
	
	return auth_util.generate_token({"user_id": dUser["id"]})
