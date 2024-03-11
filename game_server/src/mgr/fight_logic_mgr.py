# coding=utf-8
import copy
import random

import misc
from base.singleton import SingletonBase
from common import defines
from data import HeroData
from entity.common import User, HeroTeam, Hero
from entity.fight_enetity import Team, FightRoom, ExplosionBlock, MoveData, DamageData, ChessData, Fighter
from mgr.timer_mgr import TimerMgr
from sql import sqlplus
from utils import cal_util


class FightLogicMgr(SingletonBase):
	def __init__(self):
		self.default_color_dict = {}
		for i in range(defines.MAX_ATTACK_COLOR + 1):
			self.default_color_dict[i] = 0
	
	async def init_player_team(self, user_id):
		lHeroTeam = await sqlplus.list(HeroTeam, [HeroTeam.user_id == user_id, ], is_normal=False)
		if len(lHeroTeam) == 0:
			await misc.raise_exception(user_id, "队伍没有角色")
		
		
		lHero = await sqlplus.list(Hero, [Hero.user_id == user_id, ])
		dHeroList = misc.to_one_dict("id", lHero)
		
		user_hero_num_list = []
		player_hp = 0
		player_recovery = 0
		player_fighter_list = []
		lHeroTeam = sorted(lHeroTeam, key=lambda hero_team: hero_team["team_pos"])
		for dHeroTeam in lHeroTeam:
			dHero = dHeroList[dHeroTeam["hero_id"]]
			user_hero_num_list.append(dHero["hero_num"])
			player_hp += cal_util.calAttr(dHero["hero_num"], dHero["hero_grade"], "hp")
			player_recovery += cal_util.calAttr(dHero["hero_num"], dHero["hero_grade"], "recovery")
			
			fighter = Fighter()
			fighter.pos = dHeroTeam["team_pos"]
			fighter.attack = cal_util.calAttr(dHero["hero_num"], dHero["hero_grade"], "attack")
			fighter.color = HeroData.data[dHero["hero_num"]]["color"]
			fighter.hero_num = dHero["hero_num"]
			player_fighter_list.append(fighter)

		
		all_damage_list = []
		for player_fighter in player_fighter_list:
			all_damage_list.append(0)
		
		team = Team()
		team.fighter_list = player_fighter_list
		team.hp = player_hp
		team.hp_max = player_hp
		team.recovery = player_recovery
		team.all_damage_list = all_damage_list
		team.user_id = user_id
		return team
	
	def get_chess_dict(self):
		block_list = []
		chess_dict = {}
		for i in range(defines.CHESS_ROWS):
			for j in range(defines.CHESS_COLS):
				num = random.randint(0, defines.MAX_ATTACK_COLOR-1)
				for x in range(20):
					if self.check_init(i, j, num, chess_dict):
						break
					num = random.randint(0, defines.MAX_ATTACK_COLOR-1)
				chess_dict[(i, j)] = num
				block_list.append(num)
		
		chessData = ChessData()
		chessData.block_list = block_list
		chessData.chess_dict = chess_dict
		return chessData
	
	def check_init(self, i, j, num, chess_dict):  # 检测上左是否重复颜色
		if i > 0 and chess_dict[(i - 1, j)] == num:
			return False
		if j > 0 and chess_dict[(i, j - 1)] == num:
			return False
		return True
	
	def get_new_chess_dict(self, chess_dict, explosion_set) -> MoveData:
		moveData = MoveData()
		old_pos_list = []
		to_pos_list = []
		add_old_pos_list = []
		add_to_pos_list = []
		add_num_list = []
		new_chess_dict = copy.deepcopy(chess_dict)
		for j in range(defines.CHESS_COLS):
			index = 0
			for i in range(defines.CHESS_ROWS):
				old_key_pos = (i, j)
				now_key_pos = (index, j)
				if old_key_pos in explosion_set:
					continue
				
				if old_key_pos == now_key_pos:
					index += 1
					continue
				new_chess_dict[now_key_pos] = chess_dict[old_key_pos]
				old_pos_list.append(old_key_pos)
				to_pos_list.append(now_key_pos)
				index += 1
			head_index = defines.CHESS_ROWS
			for i in range(index, defines.CHESS_ROWS):
				now_key_pos = (i, j)
				old_key_pos = (head_index, j)
				num = random.randint(0, defines.MAX_ATTACK_COLOR-1)
				new_chess_dict[now_key_pos] = num
				add_old_pos_list.append(old_key_pos)
				add_to_pos_list.append(now_key_pos)
				add_num_list.append(num)
				head_index += 1
		
		moveData.old_pos_list = old_pos_list
		moveData.to_pos_list = to_pos_list
		moveData.add_old_pos_list = add_old_pos_list
		moveData.add_to_pos_list = add_to_pos_list
		moveData.add_num_list = add_num_list
		moveData.new_chess_dict = new_chess_dict
		return moveData
	
	def _union_set_list(self, all_set_list):
		list_len = len(all_set_list)
		set_list = []
		for i in range(list_len):
			set1 = all_set_list[i]
			is_union = False
			for set2 in set_list:
				if bool(set1 & set2):  # 有交集
					is_union = True
					set2.update(set1)
					break
			if not is_union:
				set_list.append(set1)
		return set_list
	
	def union_set_list(self, all_set_list):
		set_list = all_set_list
		while True:
			old_len = len(set_list)
			set_list = self._union_set_list(set_list)
			if len(set_list) == old_len:
				break
		set_list = [list(data) for data in set_list]
		return set_list
	
	def get_default_color_dict(self):
		return copy.deepcopy(self.default_color_dict)
	
	def get_explosion_list(self, chess_dict, color_dict) -> ExplosionBlock:
		pos_key_list = sorted(chess_dict.keys())
		result_set = set()
		explosionBlock = ExplosionBlock()
		
		all_set_list = []
		for pos_key in pos_key_list:
			i = pos_key[0]
			j = pos_key[1]
			explosion_set = self.get_one_explosion_list(chess_dict, i, j)
			if len(explosion_set) == 0:
				continue
			result_set = result_set.union(explosion_set)
			all_set_list.append(explosion_set)
		
		all_set_list = self.union_set_list(all_set_list)  # 炸的联通区域列表
		
		all_color_dict_list = []
		all_color_num_list = []
		all_now_color_dict_list = []
		
		for set_list in all_set_list:
			center_color = None
			now_color_dict = self.get_default_color_dict()
			for pos_key in set_list:
				center_color = chess_dict[pos_key]
				color_dict[center_color] += 1
				now_color_dict[center_color] += 1
			all_color_dict_list.append(copy.deepcopy(color_dict))  # 每个联通区炸了后加上之前的颜色珠子数汇总
			all_color_num_list.append(center_color)
			all_now_color_dict_list.append(copy.deepcopy(now_color_dict))  # 每个联通区炸了后的颜色珠子数汇总
		
		explosionBlock.all_color_num_list = all_color_num_list
		explosionBlock.all_color_dict_list = all_color_dict_list
		explosionBlock.all_now_color_dict_list = all_now_color_dict_list
		explosionBlock.all_set_list = all_set_list
		explosionBlock.block_set = result_set
		return explosionBlock
	
	def get_one_explosion_list(self, chess_dict: dict, i_start, j_start):
		center_color = chess_dict[(i_start, j_start)]
		result_set = set()
		block_set = set()
		for i in range(i_start, defines.CHESS_ROWS):  # 上遍历（包括自己）
			pos_key = (i, j_start)
			color = chess_dict.get(pos_key, None)
			if color != center_color:
				break
			block_set.add(pos_key)
		
		for i in range(i_start - 1, -1, -1):  # 下遍历
			pos_key = (i, j_start)
			color = chess_dict.get(pos_key, None)
			if color != center_color:
				break
			block_set.add(pos_key)
		if len(block_set) >= 3:
			result_set = result_set.union(block_set)
		
		block_set = set()
		for j in range(j_start, defines.CHESS_COLS):  # 右遍历（包括自己）
			pos_key = (i_start, j)
			color = chess_dict.get(pos_key, None)
			if color != center_color:
				break
			block_set.add(pos_key)
		
		for j in range(j_start - 1, -1, -1):  # 左遍历
			pos_key = (i_start, j)
			color = chess_dict.get(pos_key, None)
			if color != center_color:
				break
			block_set.add(pos_key)
		
		if len(block_set) >= 3:
			result_set = result_set.union(block_set)
		return result_set
	
	def get_attack_list(self, team: Team, all_color_dict_list: list):
		fighter_list = team.fighter_list
		all_attack_list = []
		for color_dict in all_color_dict_list:  # 每个联通区炸了后颜色珠子数汇总
			attack_list = []
			for fighter in fighter_list:
				color_num = color_dict[fighter.color]
				attack_list.append(color_num * fighter.attack)
			all_attack_list.append(attack_list)  # 每个联通区炸了后各个角色伤害数值
		return all_attack_list
	
	def get_attack_hurt_hp_list(self, team1: Team, team0: Team, color_dict: list) -> DamageData:
		fighter_list = team1.fighter_list
		hp_list = []
		damage_list = []
		damageData = DamageData()
		for fighter in fighter_list:
			color_num = color_dict[fighter.color]
			attack = color_num * fighter.attack
			hp = team0.hp - attack
			hp = max(hp, 0)
			damage = team0.hp - hp
			team0.hp = hp
			
			hp_list.append(hp)
			damage_list.append(damage)
		damageData.hp_list = hp_list
		damageData.damage_list = damage_list
		return damageData
	
	def get_enemy_attack_hurt_hp_list(self, team1: Team, team0: Team, color_amount) -> DamageData:
		fighter_list = team0.fighter_list
		hp_list = []
		damage_list = []
		damageData = DamageData()
		for fighter in fighter_list:
			attack = color_amount * fighter.attack
			hp = team1.hp - attack
			hp = max(hp, 0)
			damage = team1.hp - hp
			team1.hp = hp
			hp_list.append(hp)
			damage_list.append(damage)
		damageData.hp_list = hp_list
		damageData.damage_list = damage_list
		return damageData
	
	def get_hp_list(self, team1: Team, all_color_dict_list: list):
		hp_list = []
		for color_dict in all_color_dict_list:
			color_num = color_dict[defines.MAX_ATTACK_COLOR]
			recovery = color_num * team1.recovery
			hp = team1.hp + recovery
			hp = min(team1.hp_max, hp)
			team1.hp = hp
			hp_list.append(hp)
		return hp_list
