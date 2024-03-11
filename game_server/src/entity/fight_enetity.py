# coding=utf-8


class Fighter():
	pos: int
	attack: int
	color: int
	hero_num: int
	
class ReadyRoom():
	user_id0: int
	user_id1: int
	time: int

class Team():
	fighter_list: list
	hp: int
	hp_max: int
	recovery: int
	all_damage_list: list
	user_id: int

class FightRoom():
	team0: Team
	team1: Team
	chess_dict: dict
	is_player_round:bool
	level:int
	have_send_result0:bool
	have_send_result1:bool


class ExplosionBlock():
	block_set: set
	all_set_list: set
	all_color_dict_list: list
	all_now_color_dict_list: list
	all_color_num_list: list
class MoveData():
	old_pos_list: list
	to_pos_list: list
	add_old_pos_list: list
	add_to_pos_list: list
	add_num_list: list
	new_chess_dict: dict

class DamageData():
	hp_list:list
	damage_list:list
	
class ChessData():
	block_list = []
	chess_dict = {}