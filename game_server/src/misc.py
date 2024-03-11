# coding=utf-8
import hashlib
import inspect
import json
import random

import global_var
from base.base import AppException
from base.http_base import HttpResp
from mgr.fight_mgr import FightMgr
from mgr.ready_room_mgr import ReadyRoomMgr
from server_module import misc_logic

from utils import proto_util


def to_one_dict(key, lst):
	result = {}
	for obj in lst:
		result[obj[key]] = obj
	return result


def to_list_dict(key, lst):
	result = {}
	for obj in lst:
		if obj[key] not in result:
			result[obj[key]] = []
		result[obj[key]].append(obj)
	return result


async def send_dict(user_id, dict: dict,force_send=False):
	if force_send:
		from server_module.server import ConnMgr
		await ConnMgr.getObj().send_data(user_id, json.dumps(dict))
	else:
		from server_module import handler
		handler.g_msg_list.append((user_id, dict))
	


async def send_data(user_id, type, func, dict: dict,force_send=False):
	dict = proto_util.to_json_dict(dict)
	dict["type"] = type
	dict["func"] = func
	await send_dict(user_id, dict, force_send)


async def close_user(user_id):
	from mgr.user_mgr import UserMgr
	from server_module.server import ConnMgr
	await ConnMgr.getObj().close_conn(user_id)
	await UserMgr.getObj().removeUser(user_id)
	await FightMgr.getObj().removeFight(user_id)
	await ReadyRoomMgr.getObj().removeReadyRoom(user_id)


async def raise_exception(user_id, msg):
	await misc_logic.send_tip(user_id, msg, True)
	raise AppException(HttpResp.FAILED, msg=msg)


def is_empty(obj):
	if obj is None:
		return True
	if type(obj) is str and obj == "":
		return True
	if type(obj) is list and len(obj) == 0:
		return True
	return False


def get_rarity_key(tartget_dict,rarity_key="rarity"):
	total_rarity = 0

	for key in tartget_dict:
		data_dict = tartget_dict[key]
		total_rarity += data_dict[rarity_key]
	now_rarity = random.randint(0, total_rarity)
	key_list = list(tartget_dict.keys())
	key_list.sort()
	result_key = None
	
	total_rarity = 0
	for key in key_list:
		data_dict = tartget_dict[key]
		total_rarity += data_dict[rarity_key]
		if total_rarity >= now_rarity:
			result_key = key
			break
	return result_key
