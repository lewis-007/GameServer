# coding=utf-8

import misc
from base.singleton import SingletonBase
from entity.common import User
from entity.fight_enetity import Team, FightRoom
from mgr.ready_room_mgr import ReadyRoomMgr
from mgr.timer_mgr import TimerMgr
from server_module import misc_logic
from server_module.sender import sender_fight, sender_remote


class FightMgr(SingletonBase):
	def __init__(self):
		self.fight_dict = {}
	
	# TimerMgr.getObj().addTimer(self, "loop", 15, True)
	
	async def loop(self):
		pass
	
	def addFight(self, user_id: int, team0: Team, team1: Team, chess_dict: dict, level=None):
		fight_room = FightRoom()
		fight_room.team0 = team0
		fight_room.team1 = team1
		fight_room.chess_dict = chess_dict
		fight_room.is_player_round = True
		fight_room.level = level
		fight_room.have_send_result0 = False
		fight_room.have_send_result1 = False
		
		self.fight_dict[user_id] = fight_room
		print("当前战斗人数：", len(self.fight_dict))
	
	def addPvpFight(self, user_id0: int, user_id1: int, team0: Team, team1: Team, chess_dict: dict, level=None):
		fight_room = FightRoom()
		fight_room.team0 = team0
		fight_room.team1 = team1
		fight_room.chess_dict = chess_dict
		fight_room.is_player_round = True
		fight_room.level = level
		fight_room.have_send_result0 = False
		fight_room.have_send_result1 = False
		
		self.fight_dict[user_id0] = fight_room
		self.fight_dict[user_id1] = fight_room
		print("当前战斗人数：", len(self.fight_dict))
	
	async def removeFight(self, user_id):
		fight_room = self.fight_dict.pop(user_id, None)
		print("剩余战斗房间数：", len(self.fight_dict))
		if fight_room is None:
			return None

		if fight_room.team0.user_id is None or fight_room.team1.user_id is None :
			return None
		team = fight_room.team0
		user_id2 = fight_room.team0.user_id
		have_send_result2 = fight_room.have_send_result0
		if user_id2 == user_id:
			team = fight_room.team1
			user_id2 = fight_room.team1.user_id
			have_send_result2 = fight_room.have_send_result1
		self.fight_dict.pop(user_id2, None)

		if have_send_result2:
			return
		result_list = []
		all_damage_list = team.all_damage_list
		player_num = len(all_damage_list)
		for i in range(player_num):
			result_list.append({
				"hurt": all_damage_list[i],
				"hero_num": team.fighter_list[i].hero_num,
			})

		await sender_fight.send_open_fight_result(user_id2, True, fight_room.level, result_list, True)  # 打开结算界面
		await sender_remote.send_fight_result(user_id2, user_id, user_id2)
		
		await misc_logic.send_tip(user_id2, "对方已退出战斗",True)

	
	def getFight(self, user_id) -> FightRoom:
		return self.fight_dict.get(user_id, None)

	def getOtherUserId(self, user_id):
		fight_room = self.fight_dict.get(user_id, None)
		if fight_room is None:
			return None
		user_id2 = fight_room.team0.user_id
		if user_id2 == user_id:
			user_id2 = fight_room.team1.user_id
		return user_id2
	
	def getOtherUserTeam(self, user_id):
		fight_room = self.fight_dict.get(user_id, None)
		if fight_room is None:
			return None
		team = fight_room.team0
		user_id2 = fight_room.team0.user_id
		if user_id2 == user_id:
			team = fight_room.team1
		return team
	
	def getUserTeam(self, user_id):
		fight_room = self.fight_dict.get(user_id, None)
		if fight_room is None:
			return None
		team = fight_room.team0
		user_id2 = fight_room.team0.user_id
		if user_id2 != user_id:
			team = fight_room.team1
		return team