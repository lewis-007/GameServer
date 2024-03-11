# coding=utf-8
import random

import misc
from base.singleton import SingletonBase
from common import defines
from data import ActivitySignData, ActivityLotteryData, ShopData, GameSettingData, TaskData
from entity.common import User, UserRune
from mgr.user_mgr import UserMgr
from server_module import misc_logic
from server_module.handler_module.handler_user import HandleUser
from server_module.logic.logic_common import LogicCommon
from server_module.logic.logic_item import LogicItem
from server_module.sender import sender_user, sender_common
from sql import sqlplus
from sql.database import db
from utils import datetime_util


async def handle(data: dict):
	obj = HandleCommon.getObj()
	await getattr(obj, data["func"])(data["user_id"], data)


class HandleCommon(SingletonBase):
	async def heart(self, user_id, data):
		await UserMgr.getObj().heartUser(user_id)
	
	@db.transaction()
	async def confirm_task(self, user_id, data):
		task_data_num = data["task_data_num"]
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
		task_data = dUser["task_data"]
		task_data_len = len(TaskData.data)
		for i in range(len(task_data), task_data_len):
			task_data += "0"
		if task_data[task_data_num] == "1":
			await misc.raise_exception(user_id, "任务已完成")
		task_data = list(task_data)
		task_data[task_data_num] = "1"
		task_data = "".join(task_data)
		task_dict = TaskData.data.get(task_data_num)
		
		type = task_dict["type"]
		if type == defines.TASK_1:
			await LogicCommon.getObj().check_grade(user_id, task_dict)
		elif type == defines.TASK_2:
			await LogicCommon.getObj().check_level(user_id, dUser["level"], task_dict)
		elif type == defines.TASK_3:
			await LogicCommon.getObj().check_role(user_id, task_dict)
			
		item_dict_list = []
		rewardList = task_dict["rewardList"]
		amountList = task_dict["amountList"]
		for i in range(len(rewardList)):
			item_dict_list.append({
				"item_num": rewardList[i],
				"item_amount": amountList[i],
			})

		await misc_logic.add_item_list_play_anim(user_id, item_dict_list)
		await misc_logic.update_user_attr(user_id, "task_data", task_data)
	
	@db.transaction()
	async def buy_item(self, user_id, data):
		shop_data_num = data["shop_data_num"]
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
		
		shop_data = dUser["shop_data"]
		shop_data_len = len(ShopData.data)
		for i in range(len(shop_data), shop_data_len):
			shop_data += "0"
		if shop_data[shop_data_num] == "1":
			await misc.raise_exception(user_id, "商品已被购买")
		shop_data = list(shop_data)
		shop_data[shop_data_num] = "1"
		shop_data = "".join(shop_data)
		
		await sqlplus.update(User, {
			"shop_data": shop_data
		}, [User.id == user_id, ])
		shop_dict = ShopData.data.get(shop_data_num)
		coinType = shop_dict["coinType"]
		coinAmount = shop_dict["coinAmount"]
		itemNum = shop_dict["itemNum"]
		itemAmount = shop_dict["itemAmount"]
		
		if coinType == defines.COIN_SILVER:
			await misc_logic.down_silver_coin(user_id, coinAmount, dUser)
		elif coinType == defines.COIN_GOLD:
			await misc_logic.down_gold_coin(user_id, coinAmount, dUser)
		else:
			await misc.raise_exception(user_id, "币种错误")
		await misc_logic.add_item_play_anim(user_id, itemNum, itemAmount)
		await self.refresh_shop_dlg(user_id, None)
	
	@db.transaction()
	async def refresh_shop_item(self, user_id, data):
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
		shop_data_len = len(ShopData.data)
		shop_data = ""
		for i in range(shop_data_len):
			shop_data += "0"
		await sqlplus.update(User, {
			"shop_data": shop_data
		}, [User.id == user_id, ])
		gameSettingData = GameSettingData.data.get(0)
		await misc_logic.down_gold_coin(user_id, gameSettingData["shopGoldNum"], dUser)
		await self.refresh_shop_dlg(user_id, None)
	
	async def refresh_shop_dlg(self, user_id, data):
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
		shop_data = dUser["shop_data"]
		shop_data_len = len(ShopData.data)
		for i in range(len(shop_data), shop_data_len):
			shop_data += "0"
		
		shop_have_get_list = []
		for s in shop_data:
			shop_have_get_list.append(int(s))
		
		await sender_common.send_refresh_shop_dlg(user_id, shop_have_get_list)
	
	async def refresh_activity_lottery_dlg(self, user_id, data):
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
		last_lottery_day = dUser["last_lottery_day"]
		now_lottery_day = datetime_util.get_now_target_day()
		is_can_lottery = last_lottery_day < now_lottery_day
		await sender_common.send_refresh_activity_lottery_dlg(user_id, is_can_lottery)
	
	@db.transaction()
	async def start_lottery(self, user_id, data):
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
		
		last_lottery_day = dUser["last_lottery_day"]
		now_lottery_day = datetime_util.get_now_target_day()
		if last_lottery_day >= now_lottery_day:
			await misc.raise_exception(user_id, "今日抽奖次数已用完")
		
		await sqlplus.update(User, {
			"last_lottery_day": now_lottery_day
		}, [User.id == user_id, ])
		
		lottery_result = misc.get_rarity_key(ActivityLotteryData.data)
		print("抽奖结果：", lottery_result)
		reward_dict = ActivityLotteryData.data.get(lottery_result)
		await misc_logic.add_item(user_id, reward_dict["itemNum"], reward_dict["itemAmount"])
		await sender_common.send_refresh_activity_lottery_dlg(user_id, False)
		await sender_common.send_start_lottery(user_id, lottery_result)
	
	@db.transaction()
	async def get_sign_reward(self, user_id, data):
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
		
		today_day_num = datetime_util.get_today_day()
		last_sign_day = dUser["last_sign_day"]
		sign_count = dUser["sign_count"]
		if last_sign_day >= today_day_num:
			await misc.raise_exception(user_id, "已领取奖励")
		
		rewardData = ActivitySignData.data.get(sign_count)
		if rewardData is None:
			await misc.raise_exception(user_id, "奖励不存在")
		
		await sqlplus.update(User, {
			"last_sign_day": today_day_num,
			"sign_count": sign_count + 1,
		}, [User.id == user_id, ])
		await misc_logic.add_item_play_anim(user_id, rewardData["itemNum"], rewardData["itemAmount"])
		await self.refresh_activity_sign_dlg(user_id, None)
	
	async def refresh_activity_sign_dlg(self, user_id, data):
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
		
		today_day_num = datetime_util.get_today_day()
		is_can_get = dUser["last_sign_day"] < today_day_num
		
		await sender_common.send_refresh_activity_sign_dlg(user_id, is_can_get, dUser["sign_count"],
		                                                   datetime_util.days_of_the_month())
	
	async def open_rune_select_dlg(self, user_id, data):
		filter_user_rune_id_list = data["dlgData"].get("filter_user_rune_id_list", None)
		if misc.is_empty(filter_user_rune_id_list):
			lUserRune = await sqlplus.list(UserRune, [UserRune.user_id == user_id, UserRune.is_put == defines.FLAG_NO],
			                               is_normal=False)
		else:
			lUserRune = await sqlplus.list(UserRune, [UserRune.user_id == user_id, UserRune.is_put == defines.FLAG_NO,
			                                          UserRune.id.not_in(filter_user_rune_id_list)],
			                               is_normal=False)
		dUserRuneList = misc.to_list_dict("rune_num", lUserRune)
		lResult = []
		for key in dUserRuneList:
			lResult.append(dUserRuneList[key][0])
		await sender_common.send_open_rune_select_dlg(user_id, lResult, data.get("dlgType", None),
		                                              data.get("dlgData", None))
