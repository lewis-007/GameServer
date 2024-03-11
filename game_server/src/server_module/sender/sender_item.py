# coding=utf-8

import misc
from base.singleton import SingletonBase
from common import defines
from data import HeroData, RuneData
from entity.common import User, Hero, HeroRune, UserRune, UserItem
from mgr.user_mgr import UserMgr
from server_module import misc_logic
from server_module.logic.logic_user import LogicUser
from sql import sqlplus
from sql.database import db
from utils import item_util


async def send_del_item(user_id, user_item_id):
	await misc.send_data(user_id, defines.S2C_ITEM, "delItem", {
		"user_item_id": user_item_id,
	})


async def send_update_item_attr(user_id, user_item_id, key, value):
	await misc.send_data(user_id, defines.S2C_ITEM, "refreshItemAttr", {
		"key": key,
		"value": value,
		"user_item_id": user_item_id
	})


async def send_update_item_attr_list(user_id, lst):
	if misc.is_empty(lst):
		return
	await misc.send_data(user_id, defines.S2C_ITEM, "refreshItemAttrList", {
		"item_list": lst,
	})


async def send_add_item_list(user_id, lst):
	if misc.is_empty(lst):
		return
	await misc.send_data(user_id, defines.S2C_ITEM, "addItemList", {
		"item_list": lst,
	})


async def send_add_item_anim(user_id, lst):
	if misc.is_empty(lst):
		return
	await misc.send_data(user_id, defines.S2C_ITEM, "addItemAnim", {
		"item_num_list": lst,
	})


async def send_refresh_item_map(user_id, item_map):
	await misc.send_data(user_id, defines.S2C_ITEM, "refreshItemMap", {
		"item_map": item_map
	})
