# coding=utf-8
import copy
import random

import misc
from base.singleton import SingletonBase
from common import defines
from data import RuneForgeData, RuneData, HeroData, GameSettingData
from entity.common import User, Hero, HeroRune, UserRune, UserItem, HeroTeam
from mgr.user_mgr import UserMgr
from server_module import misc_logic
from server_module.logic.logic_hero import LogicHero
from server_module.sender import sender_hero
from sql import sqlplus
from sql.database import db


async def handle(data: dict):
	obj = HandleHero.getObj()
	await getattr(obj, data["func"])(data["user_id"], data)


class HandleHero(SingletonBase):
	
	@db.transaction()
	async def put_rune(self, user_id, data):
		hero_id = data["hero_id"]
		rune_pos = data["rune_pos"]
		new_user_rune_id = data["new_user_rune_id"]
		dUserRune = await sqlplus.getOne(UserRune, [UserRune.id == new_user_rune_id, ], is_normal=False)
		if dUserRune is None:
			return
		
		dOldHeroRune = await sqlplus.getOne(HeroRune, [HeroRune.hero_id == hero_id, HeroRune.rune_pos == rune_pos, ],
		                                    is_normal=False)
		old_hero_rune_id = None
		if dOldHeroRune is not None:  # 检查这个位置是否带有符文
			old_hero_rune_id = dOldHeroRune["id"]
			await LogicHero.getObj().save_drop_rune(dOldHeroRune["user_rune_id"])
		
		await sqlplus.update(UserRune, {
			'is_put': 1,
		}, [UserRune.id == new_user_rune_id, ], is_normal=False)
		
		hero_rune_dict = {
			"hero_id": hero_id,
			"user_rune_id": dUserRune["id"],
			"rune_pos": rune_pos,
			"rune_num": dUserRune["rune_num"],
		}
		await sqlplus.insert(HeroRune, hero_rune_dict, is_normal=False)
		
		await sender_hero.send_put_rune(user_id, hero_rune_dict, hero_id, old_hero_rune_id)
		await LogicHero.getObj().refresh_hero_fight(user_id, hero_id)
	
	@db.transaction()
	async def drop_rune(self, user_id, data):
		hero_rune_id = data["hero_rune_id"]
		dHeroRune = await sqlplus.getOne(HeroRune, [HeroRune.id == hero_rune_id, ], is_normal=False)
		if dHeroRune is None:
			return
		
		await LogicHero.getObj().save_drop_rune(dHeroRune["user_rune_id"])
		await sender_hero.send_drop_rune(user_id, dHeroRune["id"], dHeroRune["hero_id"])
		await LogicHero.getObj().refresh_hero_fight(user_id, dHeroRune["hero_id"])
	
	async def get_hero_data(self, user_id, data):
		lHero = await sqlplus.list(Hero, [Hero.user_id == user_id, ])
		if misc.is_empty(lHero):
			return
		ids = [i["id"] for i in lHero]
		lHeroRune = await sqlplus.list(HeroRune, [HeroRune.hero_id.in_(ids), ], is_normal=False)
		dHeroRuneList = misc.to_list_dict("hero_id", lHeroRune)
		
		result_hero_lst = []
		for dHero in lHero:
			lst = dHeroRuneList.get(dHero["id"], [])
			dHero["id"] = str(dHero["id"])
			dHero["user_id"] = str(dHero["user_id"])
			dHero["hero_rune_map"] = misc.to_one_dict("id", lst)
			result_hero_lst.append(dHero)
		
		await sender_hero.send_refresh_hero(user_id, misc.to_one_dict("id", result_hero_lst))
	
	@db.transaction()
	async def forge_rune(self, user_id, data):
		rune_forge_num = data["rune_forge_num"]
		rune_forge_data = RuneForgeData.data.get(rune_forge_num, None)
		if rune_forge_data is None:
			return
		# 减少神石
		await misc_logic.down_item(user_id, defines.ITEM_SHENSHI, rune_forge_data["shenShiNum"])
		runeNum = rune_forge_data["runeNum"]
		await misc_logic.add_item_play_anim(user_id, misc_logic.get_rune_item_num(runeNum), 1)
	
	async def fast_refine(self, user_id, data):
		filter_user_rune_id_list = data["filter_user_rune_id_list"]
		if misc.is_empty(filter_user_rune_id_list):
			lUserRune = await sqlplus.list(UserRune, [UserRune.user_id == user_id, UserRune.is_put == defines.FLAG_NO],
			                               is_normal=False)
		else:
			lUserRune = await sqlplus.list(UserRune, [UserRune.user_id == user_id, UserRune.is_put == defines.FLAG_NO,
			                                          UserRune.id.not_in(filter_user_rune_id_list)],
			                               is_normal=False)
		rune_data = RuneData.data
		lUserRune = sorted(lUserRune, key=lambda userRune: rune_data[userRune["rune_num"]]["runeGrade"])
		if len(lUserRune) > defines.MAX_RUNE_REFINE:
			lUserRune = lUserRune[0:defines.MAX_RUNE_REFINE]
		await sender_hero.send_fast_set_rune_button(user_id, lUserRune)
	
	@db.transaction()
	async def refine_rune(self, user_id, data):
		
		user_rune_id_list = data["user_rune_id_list"]
		if misc.is_empty(user_rune_id_list) or len(user_rune_id_list) < defines.MAX_RUNE_REFINE:
			await misc.raise_exception(user_id, "符文数量不足")
		
		lUserRune = await sqlplus.list(UserRune, [UserRune.user_id == user_id, UserRune.is_put == defines.FLAG_NO,
		                                          UserRune.id.in_(user_rune_id_list)],
		                               is_normal=False)
		if len(lUserRune) != len(user_rune_id_list):
			await misc.raise_exception(user_id, "已穿戴的符文不能提炼")

		rune_data = RuneData.data

		result_key = misc.get_rarity_key(rune_data, "runeRarity")
		if result_key is None:
			await misc.raise_exception(user_id, "提炼出错")
		
		game_data = GameSettingData.data.get(0)
		
		await misc_logic.down_item(user_id, defines.ITEM_SHENSHI, game_data["refineAmount"])  # 减少神石
		await LogicHero.getObj().down_rune(user_id, user_rune_id_list)  # 减少符文
		await misc_logic.add_item_play_anim(user_id, defines.OFFSET_RUNE2ITEM + result_key, 1)  # 增加新符文
		await misc_logic.send_tip(user_id, "获得 %s" % rune_data[result_key]["runeName"])  # 给出提示
	
	@db.transaction()
	async def summon_hero(self, user_id, data):
		is_silver = data["is_silver"]
		hero_data = copy.deepcopy(HeroData.data)
		hero_data.pop(0, None)
		hero_data.pop(1, None)
		hero_data.pop(2, None)
		total_summon_rarity = 0
		for hero_num in hero_data:
			one_hero_data = hero_data[hero_num]
			if is_silver and one_hero_data["rarity"] > 3:
				continue
			if not is_silver and one_hero_data["rarity"] < 3:
				continue
			total_summon_rarity += one_hero_data["summonRarity"]
		
		now_summon_rarity = random.randint(0, total_summon_rarity)
		total_summon_rarity = 0
		select_hero_num = None
		for hero_num in hero_data:
			one_hero_data = hero_data[hero_num]
			if is_silver and one_hero_data["rarity"] > 3:
				continue
			if not is_silver and one_hero_data["rarity"] < 3:
				continue
			total_summon_rarity += one_hero_data["summonRarity"]
			if now_summon_rarity < total_summon_rarity:
				select_hero_num = hero_num
				break
		
		if select_hero_num is None:
			await misc.raise_exception(user_id, "召唤失败")
		
		game_data = GameSettingData.data.get(0)
		# 减少硬币
		if is_silver:
			await misc_logic.down_silver_coin(user_id, game_data["silverAmount"])
		else:
			await misc_logic.down_gold_coin(user_id, game_data["goldAmount"])
		
		hero = await sqlplus.getOne(Hero, [Hero.user_id == user_id, Hero.hero_num == select_hero_num])
		if hero is None:
			hero_dict = {
				"user_id": user_id,
				"hero_num": select_hero_num,
				"hero_grade": 1,
				"hero_fight": 0,
				"hero_exp": 0,
			}
			hero_id = await sqlplus.insert(Hero, hero_dict)
			hero_dict["id"] = hero_id
			hero_fight = await LogicHero.getObj().save_hero_fight(hero_id)
			hero_dict["hero_fight"] = hero_fight
			await sender_hero.send_summon_hero(user_id, select_hero_num)
			await sender_hero.send_add_hero(user_id, hero_dict)
		else:
			game_data = GameSettingData.data.get(0)
			
			await misc_logic.add_item(user_id, defines.ITEM_SHENSHI, game_data["shenShiAmount"])
			await sender_hero.send_summon_hero(user_id, select_hero_num, "已拥有该英雄，返还神石")
	
	async def get_hero_team_data(self, user_id, data):
		lHeroTeam = await sqlplus.list(HeroTeam, [HeroTeam.user_id == user_id, ], is_normal=False)
		if misc.is_empty(lHeroTeam):
			return
		for dHeroTeam in lHeroTeam:
			dHeroTeam["id"] = str(dHeroTeam["id"])
			dHeroTeam["hero_id"] = str(dHeroTeam["hero_id"])
			dHeroTeam["user_id"] = str(dHeroTeam["user_id"])
		await sender_hero.send_refresh_hero_team(user_id, misc.to_one_dict("id", lHeroTeam))
	
	@db.transaction()
	async def add_hero_team(self, user_id, data):
		hero_id_list = data["hero_id_list"]
		if len(hero_id_list) > defines.MAX_TEAM_HERO:
			await misc.raise_exception(user_id, "阵容最多容纳%s个英雄" % defines.MAX_TEAM_HERO)
			return
		if len(hero_id_list) <= 0:
			await misc.raise_exception(user_id, "阵容最少要有1个英雄")
			return
		lHero = await sqlplus.list(Hero, [Hero.user_id == user_id, Hero.id.in_(hero_id_list)])
		if lHero is None:
			await misc.raise_exception(user_id, "英雄不存在")
			return
		if len(lHero) != len(hero_id_list):
			await misc.raise_exception(user_id, "英雄不存在")

		await sqlplus.delete(HeroTeam, [HeroTeam.user_id == user_id, ], is_normal=False)
		hero_team_lst = []
		for i in range(len(hero_id_list)):
			hero_id = hero_id_list[i]
			hero_team_lst.append({
				"hero_id":str(hero_id),
				"team_pos": i,
				"user_id": str(user_id),
			})

		await sqlplus.insert_list(HeroTeam, hero_team_lst, is_normal=False)
		await sender_hero.send_refresh_hero_team(user_id, misc.to_one_dict("id", hero_team_lst))
		await misc_logic.update_user_fight(user_id)
