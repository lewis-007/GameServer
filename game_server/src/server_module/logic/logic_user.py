# coding=utf-8

import misc
from base.singleton import SingletonBase
from common import defines
from data import HeroData, RuneData, GameSettingData
from entity.common import User, Hero, HeroRune, UserRune, UserEmail, HeroTeam
from mgr.user_mgr import UserMgr
from server_module import misc_logic
from server_module.sender import sender_user
from sql import sqlplus
from sql.database import db


class LogicUser(SingletonBase):

	async def save_rune_list(self, user_id, user_rune_num_list):  # [{"item_num":1,"item_amount":10}]
		user_rune_list = []
		for user_rune_num in user_rune_num_list:
			user_rune_list.append({
				"user_id": user_id,
				"rune_num": user_rune_num,
				"is_put": defines.FLAG_NO,
			})
		await sqlplus.insert_list(UserRune, user_rune_list, is_normal=False)
		return user_rune_list
	
	async def down_gold_coin(self, user_id, down_amount, dUser=None):
		if dUser is None:
			dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser["glod_coin"] < down_amount:
			await misc.raise_exception(user_id, "金币数量不足")
		result = dUser["glod_coin"] - down_amount
		await sqlplus.update(User, {
			"glod_coin": result
		}, [User.id == user_id, ])
		await sender_user.send_update_user_attr(user_id, "glod_coin", result)
	
	async def down_silver_coin(self, user_id, down_amount, dUser=None):
		if dUser is None:
			dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser["sliver_coin"] < down_amount:
			await misc.raise_exception(user_id, "银币数量不足")
		result = dUser["sliver_coin"] - down_amount
		await sqlplus.update(User, {
			"sliver_coin": dUser["sliver_coin"] - down_amount
		}, [User.id == user_id, ])
		await sender_user.send_update_user_attr(user_id, "sliver_coin", result)

	async def add_silver_coin(self, user_id, down_amount, dUser=None):
		if dUser is None:
			dUser = await sqlplus.getOne(User, [User.id == user_id, ])

		result = dUser["sliver_coin"] + down_amount
		await sqlplus.update(User, {
			"sliver_coin": dUser["sliver_coin"] + down_amount
		}, [User.id == user_id, ])
		await sender_user.send_update_user_attr(user_id, "sliver_coin", result)
	
	@db.transaction()
	async def add_user_exp(self, user_id, add_exp):
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		new_exp = dUser["exp"] + add_exp
		new_grade = dUser["grade"]
		game_data = GameSettingData.data.get(0)
		if new_grade >= defines.MAX_USER_GRADE:
			await misc_logic.send_tip(user_id, "已经达到等级上限")
			return
		
		while True:
			next_exp = game_data["expRadio"] * new_grade + game_data["expInit"]
			
			if new_exp < next_exp:
				break
			new_exp -= next_exp
			new_grade += 1
		if new_grade == defines.MAX_USER_GRADE:
			new_exp = 0
		
		if dUser["grade"] != new_grade:
			await misc_logic.update_user_fight(user_id)
			await misc_logic.update_user_attr(user_id,"grade",new_grade)
		await misc_logic.update_user_attr(user_id, "exp", new_exp)
		await misc_logic.send_tip(user_id, "经验提升")
	
	async def cal_user_fight(self, user_id):
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			return
		lHeroTeam = await sqlplus.list(HeroTeam, [HeroTeam.user_id == user_id, ], is_normal=False)
		id_list = [i["hero_id"] for i in lHeroTeam]
		lHero = await sqlplus.list(Hero, [Hero.id.in_(id_list), ])
		hero_fight = 0
		data = GameSettingData.data.get(0)
		
		for dHero in lHero:
			hero_fight += dHero["hero_fight"]
		fight = hero_fight + data["userFightRadio"] * dUser["level"]
		return fight

	async def update_user_fight(self, user_id):
		await misc_logic.update_user_attr(user_id, "fight", await self.cal_user_fight(user_id))
