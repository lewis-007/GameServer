# coding=utf-8
import decimal
import json
import random

import misc
from base.singleton import SingletonBase
from common import defines
from data import Level1Data, HeroData, GameSettingData
from entity.common import User, UserEmail, HeroTeam, Hero, GameQuarry
from entity.fight_enetity import Team, Fighter, ReadyRoom
from mgr.fight_logic_mgr import FightLogicMgr
from mgr.fight_mgr import FightMgr
from mgr.ready_room_mgr import ReadyRoomMgr
from mgr.user_mgr import UserMgr
from server_module import misc_logic
from server_module.logic.logic_common import LogicCommon
from server_module.logic.logic_item import LogicItem
from server_module.logic.logic_user import LogicUser
from server_module.sender import sender_common, sender_user, sender_fight, sender_remote
from sql import sqlplus
from sql.database import db
from utils import cal_util


async def handle(data: dict):
	obj = HandleFight.getObj()
	await getattr(obj, data["func"])(data["user_id"], data)


class HandleFight(SingletonBase):
	async def end_fight(self, user_id, data):
		await FightMgr.getObj().removeFight(user_id)
	
	@db.transaction()
	async def start_fight(self, user_id, data):
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
		if FightMgr.getObj().getFight(user_id) is not None:
			await misc.raise_exception(user_id, "用户已处于战斗中")
			
		level = dUser["level"]
		try:
			module_name = "data.Level%dData" % level
			module = __import__(module_name, globals=globals(), locals=locals(), fromlist=["src"])
		
		except:
			await misc.raise_exception(user_id, "关卡不存在")
		
		gameSettingData = GameSettingData.data.get(0)
		down_phy = gameSettingData["levelPhy"]
		if dUser["phy"] - down_phy < 0:  # 减少体力
			await misc.raise_exception(user_id, "体力不足")
		await misc_logic.update_user_attr(user_id, "phy", dUser["phy"] - down_phy)

		
		fight_mgr = FightLogicMgr.getObj()
		chessData = fight_mgr.get_chess_dict()
		block_list = chessData.block_list
		chess_dict = chessData.chess_dict
		
	
		enemy_hero_num_list = []
		enemy_hp = 0
		enemy_recovery = 0
		enemy_fighter_list = []
		
		
		key_list = sorted(module.data.keys())
		for key_num in key_list:
			data_dict = module.data[key_num]
			enemy_hero_num_list.append(data_dict["heroNum"])
			enemy_hp += cal_util.calAttr(data_dict["heroNum"], data_dict["grade"], "hp")
			enemy_recovery += cal_util.calAttr(data_dict["heroNum"], data_dict["grade"], "recovery")
			
			fighter = Fighter()
			fighter.pos = key_num
			fighter.attack = cal_util.calAttr(data_dict["heroNum"], data_dict["grade"], "attack")
			fighter.color = HeroData.data[data_dict["heroNum"]]["color"]
			fighter.hero_num = data_dict["heroNum"]
			enemy_fighter_list.append(fighter)
		

		team0 = Team()
		team0.fighter_list = enemy_fighter_list
		team0.hp = enemy_hp
		team0.hp_max = enemy_hp
		team0.recovery = enemy_recovery
		team0.all_damage_list = []  # 敌人伤害不统计
		team0.user_id = None
		
		team1 = await fight_mgr.init_player_team(user_id)
		
		user_hero_num_list = []
		for fighter in team1.fighter_list:
			user_hero_num_list.append(fighter.hero_num)
		FightMgr.getObj().addFight(user_id, team0, team1, chess_dict, level)
		await sender_fight.send_refresh_fight(user_id, enemy_hp, team1.hp, enemy_hero_num_list, user_hero_num_list,
		                                      block_list)
	
	async def change_block(self, user_id, data):
		i1 = data["i1"]
		j1 = data["j1"]
		i2 = data["i2"]
		j2 = data["j2"]
		
		fight_room = FightMgr.getObj().getFight(user_id)
		if fight_room is None:
			await misc.raise_exception(user_id, "房间已解散")
		old_data = fight_room.chess_dict[(i1, j1)]
		fight_room.chess_dict[(i1, j1)] = fight_room.chess_dict[(i2, j2)]
		fight_room.chess_dict[(i2, j2)] = old_data
	
	async def end_anim_round(self, user_id, data):
		fight_room = FightMgr.getObj().getFight(user_id)
		if fight_room is None:
			await misc.raise_exception(user_id, "房间已解散")

		team0 = fight_room.team0
		team1 = fight_room.team1
		result_list = []
		all_damage_list = team1.all_damage_list
		player_num = len(all_damage_list)
		
		for i in range(player_num):
			result_list.append({
				"hurt": all_damage_list[i],
				"hero_num": team1.fighter_list[i].hero_num,
			})
		
		fight_mgr = FightLogicMgr.getObj()
		if team0.hp <= 0:  # 玩家获胜
			level = fight_room.level
			reward_amount = cal_util.calAdventureReward(level)
			silver_amount = cal_util.calAdventureSilver(level)
			add_exp = cal_util.calUserLevelExp(level)
			await misc_logic.add_user_exp(user_id, add_exp)  # 增加经验
			await misc_logic.add_item_play_anim(user_id, defines.POTION_1, reward_amount)  # 增加奖励
			await misc_logic.add_silver_coin(user_id, silver_amount)  # 增加银币
			await misc_logic.update_user_attr(user_id, "level", level + 1)  # 关卡+1
			await sender_fight.send_open_fight_result(user_id, True, fight_room.level, result_list)  # 打开结算界面
			return
		elif team1.hp <= 0:
			await sender_fight.send_open_fight_result(user_id, False, fight_room.level, result_list)
			return
		
		fight_room.is_player_round = not fight_room.is_player_round
		if fight_room.is_player_round:  # 玩家回合
			await sender_fight.send_refresh_fight_round_true(user_id)
			return
		
		color_amount = 3  # 以炸了color_amount个珠子计算
		
		old_hp = team0.hp
		enemy_hp = old_hp + team0.recovery * color_amount
		enemy_hp = min(enemy_hp, team0.hp_max)
		add_hp = enemy_hp - old_hp
		team0.hp = enemy_hp
		damage_data = fight_mgr.get_enemy_attack_hurt_hp_list(team1, fight_room.team0,
		                                                      color_amount)  # 最终伤害index为对应位置的角色
		attack_hurt_hp_list = damage_data.hp_list
		await sender_fight.send_enemy_play_anim(user_id, attack_hurt_hp_list, damage_data.damage_list, add_hp, enemy_hp)
	
	async def end_round(self, user_id, data):
		fight_room = FightMgr.getObj().getFight(user_id)
		if fight_room is None:
			await misc.raise_exception(user_id, "房间已解散")
		if not fight_room.is_player_round:
			await misc.raise_exception(user_id, "对方回合")

		fight_mgr = FightLogicMgr.getObj()
		move_data_list = []
		color_dict = fight_mgr.get_default_color_dict()
		old_player_hp = fight_room.team1.hp
		while True:
			explosionBlock = fight_mgr.get_explosion_list(fight_room.chess_dict, color_dict)  # 会刷新 color_dict
			if len(explosionBlock.block_set) == 0:
				break
			explosion_list = list(explosionBlock.block_set)
			
			all_attack_list = fight_mgr.get_attack_list(fight_room.team1,
			                                            explosionBlock.all_color_dict_list)  # 每炸一个联通区域 每个角色的伤害数值
			hp_list = fight_mgr.get_hp_list(fight_room.team1,
			                                explosionBlock.all_now_color_dict_list)  # 回合者的血量变化 异常叠加了之前的血量
			moveData = fight_mgr.get_new_chess_dict(fight_room.chess_dict, explosionBlock.block_set)  # 所有珠子的移动 新增珠子的移动
			fight_room.chess_dict = moveData.new_chess_dict  # 棋盘
			
			move_data_list.append({
				"all_color_num_list": explosionBlock.all_color_num_list,
				"hp_list": hp_list,
				"all_set_list": explosionBlock.all_set_list,
				"all_attack_list": all_attack_list,
				"explosion_list": explosion_list,
				"old_pos_list": moveData.old_pos_list,
				"to_pos_list": moveData.to_pos_list,
				"add_old_pos_list": moveData.add_old_pos_list,
				"add_to_pos_list": moveData.add_to_pos_list,
				"add_num_list": moveData.add_num_list,
			})
		color_num = color_dict[defines.MAX_ATTACK_COLOR]
		if color_num == 0:
			add_hp = None
		else:
			add_hp = fight_room.team1.hp - old_player_hp
		
		# 这里和角色的伤害跳字（all_attack_list）不一定一样 因为可能把敌人打死了 多出的伤害不会计算汇总
		damage_data = fight_mgr.get_attack_hurt_hp_list(fight_room.team1, fight_room.team0,
		                                                color_dict)  # 最终伤害后的hp index为对应位置的角色
		attack_hurt_hp_list = damage_data.hp_list
		damage_list = damage_data.damage_list
		
		# 伤害汇总
		all_damage_list = fight_room.team1.all_damage_list
		for i in range(len(damage_list)):
			damage = damage_list[i]
			all_damage_list[i] += damage
		fight_room.team1.all_damage_list = all_damage_list
		
		await sender_fight.send_play_anim(user_id, move_data_list, attack_hurt_hp_list, damage_list, add_hp)
		
	async def fight_friend(self, user_id, data):
		friend_user_id = data["friend_user_id"]
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
			
		dFriendUser = await UserMgr.getObj().getUser(friend_user_id)
		if dFriendUser is None:
			await misc.raise_exception(user_id, "玩家不在线")

		await sender_fight.send_fight_friend(friend_user_id, user_id, dUser["user_name"])
		await ReadyRoomMgr.getObj().addReadyRoom(user_id)
		await misc_logic.send_tip(user_id, "发送成功")

	async def cancel_fight_friend(self, user_id, data):
		friend_user_id = data["friend_user_id"]
		ready_room = await ReadyRoomMgr.getObj().getReadyRoom(friend_user_id)
		if ready_room is None:
			await misc.raise_exception(user_id, "房间不存在")
		await misc_logic.send_tip(friend_user_id, "对方拒绝请求")
		await ReadyRoomMgr.getObj().removeReadyRoom(friend_user_id)
	
#-------------------------pvp-----------------------------

	async def confirm_fight_friend(self, user_id, data):
		friend_user_id = data["friend_user_id"]
		ready_room = await ReadyRoomMgr.getObj().getReadyRoom(friend_user_id)
		if ready_room is None:
			await misc.raise_exception(user_id, "房间不存在")
		
		
		if FightMgr.getObj().getFight(user_id) is not None:
			await misc.raise_exception(user_id, "用户已处于战斗中")
		if FightMgr.getObj().getFight(friend_user_id) is not None:
			await misc.raise_exception(friend_user_id, "用户已处于战斗中")
		
		dUser0 = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser0 is None:
			await misc.raise_exception(user_id, "用户不存在")
		
		dUser1 = await sqlplus.getOne(User, [User.id == friend_user_id, ])
		if dUser1 is None:
			await misc.raise_exception(friend_user_id, "用户不存在")
		
		fight_mgr = FightLogicMgr.getObj()
		chessData = fight_mgr.get_chess_dict()
		block_list = chessData.block_list
		chess_dict = chessData.chess_dict
		
		team0 = await fight_mgr.init_player_team(user_id)
		team1 = await fight_mgr.init_player_team(friend_user_id)
		
		FightMgr.getObj().addPvpFight(user_id, friend_user_id, team0, team1, chess_dict)
		
		hero_num_list0 = []
		for fighter in team0.fighter_list:
			hero_num_list0.append(fighter.hero_num)
		
		hero_num_list1 = []
		for fighter in team1.fighter_list:
			hero_num_list1.append(fighter.hero_num)
		
		await sender_fight.send_start_pvp_fight(user_id, team1.hp, team0.hp, hero_num_list1, hero_num_list0,
		                                        block_list,True)
		await sender_fight.send_start_pvp_fight(friend_user_id, team0.hp, team1.hp, hero_num_list0, hero_num_list1,
		                                        block_list,False)
		await ReadyRoomMgr.getObj().removeReadyRoom(friend_user_id)
	
	async def change_block_pvp(self, user_id, data):
		i1 = data["i1"]
		j1 = data["j1"]
		i2 = data["i2"]
		j2 = data["j2"]
		
		fight_room = FightMgr.getObj().getFight(user_id)
		if fight_room is None:
			await misc.raise_exception(user_id, "房间已解散")
		old_data = fight_room.chess_dict[(i1, j1)]
		fight_room.chess_dict[(i1, j1)] = fight_room.chess_dict[(i2, j2)]
		fight_room.chess_dict[(i2, j2)] = old_data
		await sender_fight.send_change_block(FightMgr.getObj().getOtherUserId(user_id),i1,j1,i2,j2)
	
	async def select_block(self, user_id, data):
		i = data["i"]
		j = data["j"]
		fight_room = FightMgr.getObj().getFight(user_id)
		if fight_room is None:
			await misc.raise_exception(user_id, "房间已解散")
		
		await sender_fight.send_select_block(FightMgr.getObj().getOtherUserId(user_id), i, j)
	
	async def end_select_block(self, user_id, data):
		fight_room = FightMgr.getObj().getFight(user_id)
		if fight_room is None:
			await misc.raise_exception(user_id, "房间已解散")
		
		await sender_fight.send_end_select_block(FightMgr.getObj().getOtherUserId(user_id))

	async def move_select_block(self, user_id, data):
		x = data["x"]
		y = data["y"]

		fight_room = FightMgr.getObj().getFight(user_id)
		if fight_room is None:
			await misc.raise_exception(user_id, "房间已解散")

		await sender_fight.send_move_select_block(FightMgr.getObj().getOtherUserId(user_id), x, y)
	
	async def end_round_pvp(self, user_id, data):
		fight_room = FightMgr.getObj().getFight(user_id)
		if fight_room is None:
			await misc.raise_exception(user_id, "房间已解散")
		be_attack_team = FightMgr.getObj().getOtherUserTeam(user_id)
		attack_team = FightMgr.getObj().getUserTeam(user_id)
		
		fight_mgr = FightLogicMgr.getObj()
		move_data_list = []
		color_dict = fight_mgr.get_default_color_dict()
		old_player_hp = attack_team.hp
		while True:
			explosionBlock = fight_mgr.get_explosion_list(fight_room.chess_dict, color_dict)  # 会刷新 color_dict
			if len(explosionBlock.block_set) == 0:
				break
			explosion_list = list(explosionBlock.block_set)
			
			all_attack_list = fight_mgr.get_attack_list(attack_team,
			                                            explosionBlock.all_color_dict_list)  # 每炸一个联通区域 每个角色的伤害数值
			hp_list = fight_mgr.get_hp_list(attack_team,
			                                explosionBlock.all_now_color_dict_list)  # 回合者的血量变化 异常叠加了之前的血量
			moveData = fight_mgr.get_new_chess_dict(fight_room.chess_dict, explosionBlock.block_set)  # 所有珠子的移动 新增珠子的移动
			fight_room.chess_dict = moveData.new_chess_dict  # 棋盘
			
			move_data_list.append({
				"all_color_num_list": explosionBlock.all_color_num_list,
				"hp_list": hp_list,
				"all_set_list": explosionBlock.all_set_list,
				"all_attack_list": all_attack_list,
				"explosion_list": explosion_list,
				"old_pos_list": moveData.old_pos_list,
				"to_pos_list": moveData.to_pos_list,
				"add_old_pos_list": moveData.add_old_pos_list,
				"add_to_pos_list": moveData.add_to_pos_list,
				"add_num_list": moveData.add_num_list,
			})
		color_num = color_dict[defines.MAX_ATTACK_COLOR]
		if color_num == 0:
			add_hp = None
		else:
			add_hp = attack_team.hp - old_player_hp
		
		# 这里和角色的伤害跳字（all_attack_list）不一定一样 因为可能把敌人打死了 多出的伤害不会计算汇总
		damage_data = fight_mgr.get_attack_hurt_hp_list(attack_team, be_attack_team,
		                                                color_dict)  # 最终伤害后的hp index为对应位置的角色
		attack_hurt_hp_list = damage_data.hp_list
		damage_list = damage_data.damage_list
		
		# 伤害汇总
		all_damage_list = attack_team.all_damage_list
		for i in range(len(damage_list)):
			damage = damage_list[i]
			all_damage_list[i] += damage
		attack_team.all_damage_list = all_damage_list
		
		await sender_fight.send_play_anim(user_id, move_data_list, attack_hurt_hp_list, damage_list, add_hp)
		await sender_fight.send_play_enemy_anim(FightMgr.getObj().getOtherUserId(user_id), move_data_list, attack_hurt_hp_list, damage_list, add_hp)
	
	async def end_anim_round_pvp(self, user_id, data):
		fight_room = FightMgr.getObj().getFight(user_id)
		if fight_room is None:
			await misc.raise_exception(user_id, "房间已解散")
		
		be_attack_team = FightMgr.getObj().getOtherUserTeam(user_id)
		attack_team = FightMgr.getObj().getUserTeam(user_id)
		

		attack_result_list = []
		all_damage_list = attack_team.all_damage_list
		player_num = len(all_damage_list)
		
		for i in range(player_num):
			attack_result_list.append({
				"hurt": all_damage_list[i],
				"hero_num": attack_team.fighter_list[i].hero_num,
			})
		
		be_attack_result_list = []
		all_damage_list = be_attack_team.all_damage_list
		player_num = len(all_damage_list)
		
		for i in range(player_num):
			be_attack_result_list.append({
				"hurt": all_damage_list[i],
				"hero_num": be_attack_team.fighter_list[i].hero_num,
			})

		if be_attack_team.hp <= 0:  # 玩家获胜
			fight_room.have_send_result0 = True
			fight_room.have_send_result1 = True
			await sender_fight.send_open_fight_result(user_id, True, fight_room.level, attack_result_list)  # 打开结算界面
			await sender_fight.send_open_fight_result(FightMgr.getObj().getOtherUserId(user_id), False, fight_room.level,
			                                          be_attack_result_list)  # 打开结算界面
			await sender_remote.send_fight_result(user_id, FightMgr.getObj().getOtherUserId(user_id), user_id)
			return
		elif attack_team.hp <= 0:
			fight_room.have_send_result0 = True
			fight_room.have_send_result1 = True
			await sender_fight.send_open_fight_result(user_id, False, fight_room.level, attack_result_list)  # 打开结算界面
			await sender_fight.send_open_fight_result(FightMgr.getObj().getOtherUserId(user_id), True, fight_room.level,
			                                          be_attack_result_list)  # 打开结算界面
			await sender_remote.send_fight_result(user_id, FightMgr.getObj().getOtherUserId(user_id), FightMgr.getObj().getOtherUserId(user_id))
			return
		
		await sender_fight.send_refresh_fight_round_true(FightMgr.getObj().getOtherUserId(user_id))
	
	async def start_match(self, user_id, data):
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
		dGameQuarry = await sqlplus.getOne(GameQuarry, [GameQuarry.user_id == user_id, ],is_normal=False)
		
		if dGameQuarry is None:
			await misc.raise_exception(user_id, "材料不足")

		if dGameQuarry["total_number"] < decimal.Decimal("0.1"):
			await misc.raise_exception(user_id, "材料不足")
		if FightMgr.getObj().getFight(user_id) is not None:
			await misc.raise_exception(user_id, "用户已处于战斗中")
		
		ready_room = await ReadyRoomMgr.getObj().getCanStartRoom()
		if ready_room is None:
			await ReadyRoomMgr.getObj().addReadyRoom(user_id)
			await sender_fight.send_open_match_dlg(user_id)
			return
		
		await sender_fight.send_close_match_fight(ready_room.user_id0)
		await self.confirm_fight_friend(user_id, {
			"friend_user_id": ready_room.user_id0,
		})
	
	async def cancel_match(self, user_id, data):
		
		await ReadyRoomMgr.getObj().removeReadyRoom(user_id)
		await sender_fight.send_close_match_fight(user_id)
