# coding=utf-8

import misc
from base.singleton import SingletonBase
from common import defines
from data import HeroData, RuneData
from entity.common import User, Hero, HeroRune, UserRune, UserEmail
from mgr.user_mgr import UserMgr
from sql import sqlplus
from sql.database import db


async def send_refresh_email(user_id, user_email_map):
	await misc.send_data(user_id, defines.S2C_USER, "refreshEmail", {
		"user_email_map": user_email_map
	})


async def send_refresh_user(user_id, dUser):
	if dUser is None:
		return
	await misc.send_data(user_id, defines.S2C_USER, "refreshUser", dUser)


async def send_update_user_email_attr(user_id, user_email_id, key, value):
	await misc.send_data(user_id, defines.S2C_USER, "refresUserEmailAttr", {
		"key": key,
		"value": value,
		"user_email_id": user_email_id
	})


async def send_del_user_email(user_id, user_email_id):
	await misc.send_data(user_id, defines.S2C_USER, "delUserEmail", {
		"user_email_id": user_email_id
	})


async def send_add_user_email(user_id, user_email_dict):
	await misc.send_data(user_id, defines.S2C_USER, "addUserEmail", {
		"user_email": user_email_dict
	})



async def send_update_user_attr(user_id, key, value):
	await misc.send_data(user_id, defines.S2C_USER, "refreshUserAttr", {
		"key": key,
		"value": value
	})
	

async def send_grade_rank(user_id, lUser):
	await misc.send_data(user_id, defines.S2C_USER, "refreshGradeRank", {
		"lUser": lUser
	})
	
async def send_fight_rank(user_id, lUser):
	await misc.send_data(user_id, defines.S2C_USER, "refreshFightRank", {
		"lUser": lUser
	})

async def send_refresh_user_friend_req(user_id, user_data_list):
	await misc.send_data(user_id, defines.S2C_USER, "refreshUserFriendReq", {
		"user_data_list": user_data_list
	})

async def send_refresh_user_friend(user_id, user_data_list):
	await misc.send_data(user_id, defines.S2C_USER, "refreshUserFriend", {
		"user_data_list": user_data_list
	})

async def send_refresh_find_user(user_id, user_data_list):
	await misc.send_data(user_id, defines.S2C_USER, "refreshFindUser", {
		"user_data_list": user_data_list
	})