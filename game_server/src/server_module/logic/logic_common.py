# coding=utf-8
import math

import misc
from base.singleton import SingletonBase
from common import defines
from data import HeroData, RuneData, ShopData, TaskData
from entity.common import User, Hero, HeroRune, UserRune
from mgr.user_mgr import UserMgr

from sql import sqlplus
from sql.database import db


class LogicCommon(SingletonBase):
	async def check_grade(self, user_id, task_dict: dict):
		lHero = await sqlplus.list(Hero, [Hero.user_id == user_id, ])
		value = 0
		for dHero in lHero:
			if dHero["hero_grade"] >= task_dict["grade"]:
				value += 1
		if value >= task_dict["roleNum"]:
			return
		await misc.raise_exception(user_id, "角色数量不足")
	
	async def check_level(self, user_id, level, task_dict: dict):
		if level >= task_dict["level"]:
			return
		await misc.raise_exception(user_id, "通关关卡数不足")
	
	async def check_role(self, user_id, task_dict: dict):
		lHero = await sqlplus.list(Hero, [Hero.user_id == user_id, ])
		if len(lHero) >= task_dict["roleGetNum"]:
			return
		await misc.raise_exception(user_id, "拥有角色数量不足")
	
	async def day_refresh_user_login(self):
		print("重置用户日首次登录")
		lUser = await sqlplus.list(User)
		for dUser in lUser:
			dUser["is_first_day_login"] = defines.FLAG_YES
		await sqlplus.update_list(User, lUser)
	
	async def month_refresh_user_login(self):
		print("重置用户月首次登录")
		lUser = await sqlplus.list(User)
		
		for dUser in lUser:
			dUser["is_first_month_login"] = defines.FLAG_YES
		await sqlplus.update_list(User, lUser)
