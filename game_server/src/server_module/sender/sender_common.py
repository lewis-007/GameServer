# coding=utf-8

import misc
from base.singleton import SingletonBase
from common import defines
from data import HeroData, RuneData
from entity.common import User, Hero, HeroRune, UserRune
from mgr.user_mgr import UserMgr
from sql import sqlplus
from sql.database import db


async def send_tip(user_id, msg, force_send=False):
	await misc.send_data(user_id, defines.S2C_COMMON, "openCommon_BubbleTipDlg", {
		"msg": msg,
	}, force_send)


async def send_open_rune_select_dlg(user_id, lUserRune, dlgType, dlgData):
	await misc.send_data(user_id, defines.S2C_COMMON, "openRuneSelectDlg", {
		"userRuneList": lUserRune,
		"dlgType": dlgType,
		"dlgData": dlgData,
	})


async def send_refresh_activity_sign_dlg(user_id, is_can_get, sign_count, day_num):
	await misc.send_data(user_id, defines.S2C_COMMON, "refreshActivitySignDlg", {
		"is_can_get": is_can_get,
		"sign_count": sign_count,
		"day_num": day_num,
	})

async def send_start_lottery(user_id, lottery_result):
	await misc.send_data(user_id, defines.S2C_COMMON, "startLottery", {
		"lottery_result": lottery_result,
	})
	
async def send_refresh_activity_lottery_dlg(user_id, is_can_lottery):
	await misc.send_data(user_id, defines.S2C_COMMON, "refreshActivityLotteryDlg", {
		"is_can_lottery": is_can_lottery,
	})

async def send_refresh_shop_dlg(user_id, shop_have_get_list):
	await misc.send_data(user_id, defines.S2C_COMMON, "refreshShopDlg", {
		"shop_have_get_list": shop_have_get_list,
	})

