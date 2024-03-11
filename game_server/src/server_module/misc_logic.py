# coding=utf-8
from common import defines
from entity.common import User
from server_module.logic.logic_item import LogicItem

# 保存、发送物品
from server_module.logic.logic_user import LogicUser
from server_module.sender import sender_item, sender_common, sender_user
from sql import sqlplus


async def add_item_list(user_id, item_dict_list):  # [{"item_num":1,"item_amount":10}]
	await LogicItem.getObj().add_item_list(user_id, item_dict_list)


async def down_gold_coin(user_id, down_amount, dUser=None):
	await LogicUser.getObj().down_gold_coin(user_id, down_amount, dUser)


async def down_silver_coin(user_id, down_amount, dUser=None):
	await LogicUser.getObj().down_silver_coin(user_id, down_amount, dUser)
	
async def add_silver_coin(user_id, down_amount, dUser=None):
	await LogicUser.getObj().add_silver_coin(user_id, down_amount, dUser)


# 保存、发送物品、播放动画
async def add_item_list_play_anim(user_id, item_dict_list):  # [{"item_num":1,"item_amount":10}]
	await add_item_list(user_id, item_dict_list)
	item_data_list = [i["item_num"] for i in item_dict_list]
	await sender_item.send_add_item_anim(user_id, item_data_list)


async def add_item(user_id, item_num, item_amount):  # [{"item_num":1,"item_amount":10}]
	await add_item_list(user_id, [{
		"item_num": item_num, "item_amount": item_amount
	}])


async def add_item_play_anim(user_id, item_num, item_amount):  # [{"item_num":1,"item_amount":10}]
	await add_item_list_play_anim(user_id, [{
		"item_num": item_num, "item_amount": item_amount
	}])


async def down_item(user_id, user_item_num=None, down_amount=1, dUserItem=None):
	await LogicItem.getObj().down_item(user_id, user_item_num, down_amount, dUserItem)


async def send_tip(user_id, msg: str, force_send=False):
	await sender_common.send_tip(user_id, msg, force_send)


def get_rune_id(rune_num):
	return defines.OFFSET_RUNE2ITEM + rune_num + 2 ** 53 - 1


def get_rune_item_num(rune_num):
	return defines.OFFSET_RUNE2ITEM + rune_num


async def update_user_fight(user_id):
	await LogicUser.getObj().update_user_fight(user_id)

async def update_user_attr(user_id, key, value):
	await sqlplus.update(User, {
		key: value
	}, [User.id == user_id, ])
	await sender_user.send_update_user_attr(user_id, key, value)

async def add_user_exp(user_id, add_exp):
	await LogicUser.getObj().add_user_exp(user_id, add_exp)