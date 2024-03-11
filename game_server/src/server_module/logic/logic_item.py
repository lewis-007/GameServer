# coding=utf-8

import misc
from base.base import AppException
from base.http_base import HttpResp
from base.singleton import SingletonBase
from common import defines
from data import HeroData, RuneData
from entity.common import User, Hero, HeroRune, UserRune, UserItem
from mgr.user_mgr import UserMgr
from server_module import misc_logic
from server_module.logic.logic_user import LogicUser
from server_module.sender import sender_item
from sql import sqlplus
from sql.database import db
from utils import item_util


class LogicItem(SingletonBase):

	async def _add_rune(self, user_id, item_dict_list):
		if misc.is_empty(item_dict_list):
			return
		user_rune_list_dict = misc.to_list_dict("item_num", item_dict_list)
		
		user_rune_dict = {}
		user_rune_num_list = []
		for item_num in user_rune_list_dict:
			item_amount = 0
			user_rune_list = user_rune_list_dict[item_num]
			for item_dict in user_rune_list:
				item_amount += item_dict["item_amount"]
			user_rune_dict[item_num] = item_amount
			for i in range(item_amount):
				user_rune_num_list.append(item_num - defines.OFFSET_RUNE2ITEM)
		
		lOldUserRune = await sqlplus.list(UserRune, [UserRune.user_id == user_id, ],
		                                        is_normal=False)
		dOldUserRuneList = misc.to_list_dict("rune_num", lOldUserRune)
		
		await LogicUser.getObj().save_rune_list(user_id, user_rune_num_list)
		insert_user_item_list_result = []
		update_user_item_list_result = []
		for item_num in user_rune_dict:
			add_amount = user_rune_dict[item_num]
			rune_num = item_num - defines.OFFSET_RUNE2ITEM
			if rune_num in dOldUserRuneList:  # 原本已经拥有的
				update_user_item_list_result.append({
					"item_id": misc_logic.get_rune_id(rune_num),
					"key": "item_amount",
					"value": add_amount + len(dOldUserRuneList[rune_num]),
				})
			else:
				insert_user_item_list_result.append({
					"id": misc_logic.get_rune_id(rune_num),
					"user_id": user_id,
					"item_num": item_num,
					"item_amount": add_amount,
				})
		
		await sender_item.send_add_item_list(user_id, insert_user_item_list_result)
		await sender_item.send_update_item_attr_list(user_id, update_user_item_list_result)
	
	async def _add_item(self, user_id, item_dict_list):
		item_data_dict = {}
		if misc.is_empty(item_dict_list):
			return
		
		for item_dict in item_dict_list:
			item_num = item_dict["item_num"]
			if item_num not in item_data_dict:
				item_data_dict[item_num] = item_dict["item_amount"]
			else:
				item_data_dict[item_num] += item_dict["item_amount"]
		item_num_list = item_data_dict.keys()
		lUserItem = await sqlplus.list(UserItem,
		                                    [UserItem.user_id == user_id, UserItem.item_num.in_(item_num_list), ],
		                                    is_normal=False)
		
		user_item_num_dict = {}
		if not misc.is_empty(lUserItem):
			user_item_num_dict = misc.to_one_dict("item_num", lUserItem)
		
		update_user_item_list = []
		update_user_data_list = []
		
		insert_user_item_list = []
		for item_num in item_data_dict:
			item_amount = item_data_dict[item_num]
			if item_num in user_item_num_dict:
				old_item_dict = user_item_num_dict[item_num]
				old_item_dict["item_amount"] += item_amount
				update_user_item_list.append(old_item_dict)
				update_user_data_list.append({
					"item_id": old_item_dict["id"],
					"key": "item_amount",
					"value": old_item_dict["item_amount"],
				})
			else:
				insert_user_item_list.append({
					"user_id": user_id,
					"item_num": item_num,
					"item_amount": item_amount,
				})
		
		await sqlplus.update_list(UserItem, update_user_item_list, is_normal=False)
		await sqlplus.insert_list(UserItem, insert_user_item_list, is_normal=False)
		
		await sender_item.send_update_item_attr_list(user_id, update_user_data_list)
		
		insert_user_item_list_result = []
		for item_dict in insert_user_item_list:
			insert_user_item_list_result.append(item_dict)
		await sender_item.send_add_item_list(user_id, insert_user_item_list_result)
	
	@db.transaction()
	async def add_item_list(self, user_id, item_dict_list):  # [{"item_num":1,"item_amount":10}]
		rune_item_list = []
		last_item_list = []
		for data in item_dict_list:
			item_num = data["item_num"]
			if item_util.check_is_rune_item(item_num):
				rune_item_list.append(data)
			else:
				last_item_list.append(data)
		await self._add_rune(user_id, rune_item_list)
		await self._add_item(user_id, last_item_list)

	@db.transaction()
	async def down_item(self, user_id, user_item_num= None, down_amount=1, dUserItem=None):
		if user_item_num is not None:
			dUserItem = await sqlplus.getOne(UserItem, [UserItem.item_num == user_item_num, ], is_normal=False)
			if dUserItem is None:
				await misc.raise_exception(user_id, "物品数量不足")
		
		user_item_id = dUserItem["id"]
		last_item_amount = dUserItem["item_amount"]
		if last_item_amount > down_amount:
			amount = last_item_amount - down_amount
			item_dict = {
				"item_amount": amount
			}
			await sqlplus.update(UserItem, item_dict, [UserItem.id == user_item_id, ], is_normal=False)
			await sender_item.send_update_item_attr(user_id, user_item_id, "item_amount", amount)
		elif last_item_amount == down_amount:
			await sqlplus.delete(UserItem, [UserItem.id == user_item_id, ], is_normal=False)
			await sender_item.send_del_item(user_id, user_item_id)
		else:
			await misc.raise_exception(user_id, "物品数量不足")

