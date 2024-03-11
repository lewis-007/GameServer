# coding=utf-8

import misc
from base.singleton import SingletonBase
from common import defines
from data import HeroData, RuneData
from entity.common import User, Hero, HeroRune, UserRune, UserEmail
from mgr.user_mgr import UserMgr
from sql import sqlplus
from sql.database import db


async def send_refresh_fight(user_id, enemy_hp, player_hp, enemy_hero_num_list, user_hero_num_list, block_list):
	await misc.send_data(user_id, defines.S2C_FIGHT, "refreshFight", {
		"enemy_hp": enemy_hp,
		"player_hp": player_hp,
		"enemy_hero_num_list": enemy_hero_num_list,
		"user_hero_num_list": user_hero_num_list,
		"block_list": block_list,
	})


async def send_refresh_fight_round_true(user_id):
	await misc.send_data(user_id, defines.S2C_FIGHT, "refreshFightRoundTrue", {
	})


async def send_play_anim(user_id, move_data_list, attack_hurt_hp_list, damage_list, add_hp):
	await misc.send_data(user_id, defines.S2C_FIGHT, "playAnim", {
		"move_data_list": move_data_list,
		"attack_hurt_hp_list": attack_hurt_hp_list,
		"damage_list": damage_list,
		"add_hp": add_hp,
	})
	
async def send_enemy_play_anim(user_id, attack_hurt_hp_list,damage_list, add_hp,enemy_hp):
	await misc.send_data(user_id, defines.S2C_FIGHT, "playEnemyAnim", {
		"attack_hurt_hp_list": attack_hurt_hp_list,
		"damage_list": damage_list,
		"add_hp": add_hp,
		"enemy_hp": enemy_hp,
	})

async def send_open_fight_result(user_id,is_win,level, result_list,force_send=False):
	await misc.send_data(user_id, defines.S2C_FIGHT, "openFightResult", {
		"is_win": is_win,
		"level": level,
		"result_list": result_list,
	},force_send)
	
async def send_fight_friend(user_id,friend_id,user_name):
	await misc.send_data(user_id, defines.S2C_FIGHT, "fightFriend", {
		"friend_id": friend_id,
		"user_name": user_name,
	})

#-----------------------------PVP----------------------------
async def send_start_pvp_fight(user_id, enemy_hp, player_hp, enemy_hero_num_list, user_hero_num_list, block_list,is_round):
	await misc.send_data(user_id, defines.S2C_FIGHT, "startPvpFight", {
		"enemy_hp": enemy_hp,
		"player_hp": player_hp,
		"enemy_hero_num_list": enemy_hero_num_list,
		"user_hero_num_list": user_hero_num_list,
		"block_list": block_list,
		"is_round": is_round,
	})

async def send_change_block(user_id, i1,j1,i2,j2):
	await misc.send_data(user_id, defines.S2C_FIGHT, "changeBlock", {
		"user_id": user_id,
		"i1": i1,
		"j1": j1,
		"i2": i2,
		"j2": j2,
	})
	
async def send_select_block(user_id, i,j):
	await misc.send_data(user_id, defines.S2C_FIGHT, "selectBlock", {
		"user_id": user_id,
		"i": i,
		"j": j,

	})

async def send_end_select_block(user_id):
	await misc.send_data(user_id, defines.S2C_FIGHT, "endSelectBlock", {
		"user_id": user_id,
	})

async def send_move_select_block(user_id, x,y):
	await misc.send_data(user_id, defines.S2C_FIGHT, "moveSelectBlock", {
		"user_id": user_id,
		"x": x,
		"y": y,

	})


async def send_play_enemy_anim(user_id, move_data_list, attack_hurt_hp_list, damage_list, add_hp):
	await misc.send_data(user_id, defines.S2C_FIGHT, "playEnemyAnimPVP", {
		"move_data_list": move_data_list,
		"attack_hurt_hp_list": attack_hurt_hp_list,
		"damage_list": damage_list,
		"add_hp": add_hp,
	})

async def send_open_match_dlg(user_id):
	await misc.send_data(user_id, defines.S2C_FIGHT, "openMatchDlg", {
	
	})


async def send_close_match_fight(user_id):
	await misc.send_data(user_id, defines.S2C_FIGHT, "closeMatchDlg", {
	})