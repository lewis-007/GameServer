# coding=utf-8

import misc
from base.singleton import SingletonBase
from common import defines
from data import GameSettingData
from entity.common import User, UserItem, Hero, UserRune
from mgr.user_mgr import UserMgr
from server_module import misc_logic
from server_module.logic.logic_common import LogicCommon
from server_module.logic.logic_hero import LogicHero
from server_module.logic.logic_item import LogicItem
from server_module.sender import sender_common, sender_hero, sender_item
from sql import sqlplus
from sql.database import db


async def handle(data: dict):
	obj = HandleItem.getObj()
	await getattr(obj, data["func"])(data["user_id"], data)


class HandleItem(SingletonBase):
	async def get_item_data(self, user_id, data):
		
		lUserItem = await sqlplus.list(UserItem, [UserItem.user_id == user_id, ], is_normal=False)
		result_item_list = []
		for dUserItem in lUserItem:
			result_item_list.append(dUserItem)
		
		lUserRune = await sqlplus.list(UserRune, [UserRune.user_id == user_id, ],
		                                    is_normal=False)
		dUserRuneList = misc.to_list_dict("rune_num", lUserRune)
		for rune_num in dUserRuneList:
			user_rune_list2 = dUserRuneList[rune_num]
			user_rune_dict = user_rune_list2[0]
			
			result_item_list.append({
				"id": misc_logic.get_rune_id(user_rune_dict["rune_num"]),
				"user_id": user_rune_dict["user_id"],
				"item_num": defines.OFFSET_RUNE2ITEM + user_rune_dict["rune_num"],
				"item_amount": len(user_rune_list2),
			})

		await sender_item.send_refresh_item_map(user_id, misc.to_one_dict("id", result_item_list))
	
	@db.transaction()
	async def use_potion(self, user_id, data):
		user_item_id = data["user_item_id"]
		hero_id = data["hero_id"]
		dUserItem = await sqlplus.getOne(UserItem, [UserItem.user_id == user_id, UserItem.id == user_item_id, ], is_normal=False)
		if dUserItem is None:
			await misc_logic.send_tip(user_id, "物品数量不足")
			return
		
		if dUserItem["item_num"] not in defines.ITEM_POTION_NUM_DATA:
			await misc_logic.send_tip(user_id, "物品无法使用")
			return
		add_exp = defines.ITEM_POTION_NUM_DATA[dUserItem["item_num"]]
		dHero = await sqlplus.getOne(Hero, [Hero.id == hero_id, ])
		new_exp = dHero["hero_exp"] + add_exp
		new_grade = dHero["hero_grade"]
		game_data = GameSettingData.data.get(0)
		if new_grade >= defines.MAX_HERO_GRADE:
			await misc_logic.send_tip(user_id, "已经达到等级上限")
			return
		
		while True:
			next_exp = game_data["heroExpRadio"] * new_grade + game_data["heroExpInit"]
			
			if new_exp < next_exp:
				break
			new_exp -= next_exp
			new_grade += 1
		if new_grade == defines.MAX_HERO_GRADE:
			new_exp = 0
		
		if dHero["hero_grade"] != new_grade:
			hero_dict = {
				"hero_grade": new_grade
			}
			await sqlplus.update(Hero, hero_dict, [Hero.id == hero_id, ])
			await LogicHero.getObj().refresh_hero_fight(user_id, hero_id)
		hero_dict = {
			"hero_exp": new_exp
		}
		await sqlplus.update(Hero, hero_dict, [Hero.id == hero_id, ])
		# 物品减1
		await misc_logic.down_item(user_id, dUserItem=dUserItem)

		
		# 刷新等级和经验
		if dHero["hero_grade"] != new_grade:
			await sender_hero.send_update_hero_attr(user_id, hero_id, "hero_grade", new_grade)
		await misc_logic.send_tip(user_id, "经验提升")
		await sender_hero.send_update_hero_attr(user_id, hero_id, "hero_exp", new_exp)
		await LogicHero.getObj().refresh_hero_fight(user_id, data["hero_id"])
