# coding=utf-8

import misc
from base.singleton import SingletonBase
from common import defines
from data import HeroData, RuneData
from entity.common import User, Hero, HeroRune, UserRune
from mgr.user_mgr import UserMgr
from sql import sqlplus
from sql.database import db


async def send_update_hero_attr(user_id, hero_id, key, value):
	await misc.send_data(user_id, defines.S2C_HERO, "refresHeroPropAttr", {
		"key": key,
		"value": value,
		"hero_id": hero_id
	})


async def send_put_rune(user_id, new_hero_rune, hero_id, old_hero_rune_id):
	await misc.send_data(user_id, defines.S2C_HERO, "putRune", {
		"new_hero_rune": new_hero_rune,
		"hero_id": hero_id,
		"old_hero_rune_id": old_hero_rune_id,
	})


async def send_drop_rune(user_id, hero_rune_id, hero_id):
	await misc.send_data(user_id, defines.S2C_HERO, "dropRune", {
		"hero_rune_id": hero_rune_id,
		"hero_id": hero_id
	})


async def send_refresh_hero(user_id, hero_map):
	await misc.send_data(user_id, defines.S2C_HERO, "refreshHero", {
		"hero_map": hero_map
	})

async def send_refresh_hero_team(user_id, hero_team_map):
	await misc.send_data(user_id, defines.S2C_HERO, "refreshHeroTeam", {
		"hero_team_map": hero_team_map
	})

async def send_fast_set_rune_button(user_id, lUserRune):
	await misc.send_data(user_id, defines.S2C_HERO, "fastSetRuneButton", {
		"lUserRune": lUserRune
	})
	
async def send_summon_hero(user_id, hero_num,msg=None):
	await misc.send_data(user_id, defines.S2C_HERO, "summonHero", {
		"hero_num": hero_num,
		"msg": msg
	})
	
async def send_add_hero(user_id, hero_dict):
	await misc.send_data(user_id, defines.S2C_HERO, "addHero", {
		"hero": hero_dict,
	})