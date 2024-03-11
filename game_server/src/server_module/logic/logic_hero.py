# coding=utf-8

import misc
from base.singleton import SingletonBase
from common import defines
from data import HeroData, RuneData
from entity.common import User, Hero, HeroRune, UserRune
from mgr.user_mgr import UserMgr
from server_module import misc_logic
from server_module.sender import sender_hero, sender_item
from sql import sqlplus
from sql.database import db


class LogicHero(SingletonBase):
	@db.transaction()
	async def save_drop_rune(self, user_rune_id):  # 脱下
		await sqlplus.update(UserRune, {
			'is_put': 0,
		}, [UserRune.id == user_rune_id, ], is_normal=False)
		await sqlplus.delete(HeroRune, [HeroRune.user_rune_id == user_rune_id, ], is_normal=False)
		
	
	async def save_hero_fight(self, hero_id):
		dHero = await sqlplus.getOne(Hero, [Hero.id == hero_id, ])
		if dHero is None:
			return
		data = HeroData.data.get(dHero["hero_num"], None)
		if data is None:
			return
		lHeroRune = await sqlplus.list(HeroRune, [HeroRune.hero_id == hero_id, ], is_normal=False)
		
		rune_fight = 0
		for dHeroRune in lHeroRune:
			runeData = RuneData.data.get(dHeroRune["rune_num"], None)
			if runeData is None:
				continue
			rune_fight += (runeData["runeGrade"] + 1) * 300
		
		hero_fight = dHero["hero_grade"] * data["rarity"] * 10 + rune_fight
		hero_fight = int(hero_fight)
		result_dict = {
			"hero_fight": hero_fight
		}
		await sqlplus.update(Hero, result_dict, [Hero.id == hero_id, ])
		return hero_fight
	
	async def refresh_hero_fight(self, user_id, hero_id):
		hero_fight = await self.save_hero_fight(hero_id)
		await sender_hero.send_update_hero_attr(user_id, hero_id, "hero_fight", hero_fight)
		await misc_logic.update_user_fight(user_id)
	
	async def down_rune(self, user_id, user_rune_id_list):
		lUserRune = await sqlplus.list(UserRune, [UserRune.user_id == user_id, ],
		                               is_normal=False)
		
		dUserRuneList = misc.to_one_dict("id", lUserRune)
		dUserRuneNum = misc.to_list_dict("rune_num", lUserRune)
		
		dNum = {}
		for id in user_rune_id_list:
			dUserRune = dUserRuneList[id]
			rune_num = dUserRune["rune_num"]
			if rune_num not in dNum:
				dNum[rune_num] = 0
			dNum[rune_num] += 1
		for rune_num in dNum:
			lUserRune = dUserRuneNum[rune_num]
			
			down_num = dNum[rune_num]
			if down_num > len(lUserRune):
				await misc.raise_exception(user_id, "符文数量不足")
			elif down_num == len(lUserRune):
				
				user_item_id = misc_logic.get_rune_id(rune_num)
				await sender_item.send_del_item(user_id, user_item_id)
			else:
				user_item_id = misc_logic.get_rune_id(rune_num)
				await sender_item.send_update_item_attr(user_id, user_item_id, "item_amount", len(lUserRune) - down_num)
		
		await sqlplus.delete(UserRune, [UserRune.id.in_(user_rune_id_list), ], is_normal=False)
