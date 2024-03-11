# coding=utf-8
import json

import misc
from base.base import AppException
from base.singleton import SingletonBase
from common import defines
from entity.common import User, UserEmail, UserFriendReq, UserFriend
from mgr.user_mgr import UserMgr
from server_module import misc_logic
from server_module.logic.logic_common import LogicCommon
from server_module.logic.logic_item import LogicItem
from server_module.logic.logic_user import LogicUser
from server_module.sender import sender_common, sender_user
from sql import sqlplus
from sql.database import db


async def handle(data: dict):
	obj = HandleUser.getObj()
	await getattr(obj, data["func"])(data["user_id"], data)


class HandleUser(SingletonBase):
	
	async def refresh_next_guide(self, user_id, data):
		guide = data["guide"]
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
		await misc_logic.update_user_attr(user_id,"guide",guide)
	
	async def add_friend_req(self, user_id, data):
		friend_user_id = data["friend_user_id"]
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.raise_exception(user_id, "用户不存在")
		dFriendUser = await sqlplus.getOne(User, [User.id == friend_user_id, ])
		if dFriendUser is None:
			await misc.raise_exception(user_id, "玩家不存在")

		dUserFriend = await sqlplus.getOne(UserFriend, [UserFriend.user_id == user_id,
		                                                UserFriend.friend_user_id == friend_user_id, ], is_normal=False)
		
		if dUserFriend is not None:
			await misc_logic.send_tip(user_id, "你们已经是好友")
			return
		dUserFriendReq = await sqlplus.getOne(UserFriendReq, [UserFriendReq.req_user_id == user_id,
		                                                      UserFriendReq.friend_user_id == friend_user_id])
		if dUserFriendReq is not None:
			await misc.raise_exception(user_id, "请求已经发送")
		await sqlplus.insert(UserFriendReq, {
			"req_user_id": user_id,
			"friend_user_id": friend_user_id,
		})
		await self.get_friend_req_list(friend_user_id,None)
		await misc_logic.send_tip(user_id, "发送成功")
	
	@db.transaction()
	async def confirm_friend_req(self, user_id, data):
		user_friend_req_id = data["user_friend_req_id"]
		dUserFriendReq = await sqlplus.getOne(UserFriendReq, [UserFriendReq.req_user_id == user_friend_req_id,
		                                                      UserFriendReq.friend_user_id == user_id, ])
		if dUserFriendReq is None:
			await misc.raise_exception(user_id, "该已经失效")
		dUserFriend = await sqlplus.getOne(UserFriend, [UserFriend.user_id == user_id, UserFriend.friend_user_id == user_friend_req_id, ], is_normal=False)
		await sqlplus.delete(UserFriendReq, [UserFriendReq.id == dUserFriendReq["id"], ])
		if dUserFriend is not None:
			await self.get_friend_req_list(user_id, None)
			await misc_logic.send_tip(user_id, "你们已经是好友")
			return
		lUserFriend = await sqlplus.list(UserFriend, [UserFriend.user_id == user_id, ], is_normal=False)
		if len(lUserFriend) >= defines.FIREND_NUM_MAX:
			await misc.raise_exception(user_id, "好友已达到上限")
		await sqlplus.insert(UserFriend, {
			"user_id": dUserFriendReq["req_user_id"],
			"friend_user_id": dUserFriendReq["friend_user_id"],
		}, is_normal=False)
		await sqlplus.insert(UserFriend, {
			"user_id": dUserFriendReq["friend_user_id"],
			"friend_user_id": dUserFriendReq["req_user_id"],
		}, is_normal=False)
		await self.get_friend_req_list(user_id, None)
	
	@db.transaction()
	async def cancel_friend_req(self, user_id, data):
		user_friend_req_id = data["user_friend_req_id"]
		dUserFriendReq = await sqlplus.getOne(UserFriendReq, [UserFriendReq.req_user_id == user_friend_req_id,
		                                                      UserFriendReq.friend_user_id == user_id, ])
		if dUserFriendReq is None:
			await misc.raise_exception(user_id, "该已经失效")
		await sqlplus.delete(UserFriendReq, [UserFriendReq.id == dUserFriendReq["id"], ])
		await self.get_friend_req_list(user_id, None)
	
	async def get_friend_list(self, user_id, data):
		lUserFriend = await sqlplus.list(UserFriend, [UserFriend.user_id == user_id, ], is_normal=False)
		friend_id_list = misc.to_one_dict("friend_user_id", lUserFriend)
		lUser = await sqlplus.list(User, [User.id.in_(friend_id_list), ])
		user_data_list = []
		for dUser in lUser:
			user_data_list.append({
				"id": dUser["id"],
				"grade": dUser["grade"],
				"fight": dUser["fight"],
				"level": dUser["level"],
				"user_name": dUser["user_name"],
				"icon": dUser["icon"],
			})
		await sender_user.send_refresh_user_friend(user_id, user_data_list)
	
	async def get_friend_req_list(self, user_id, data):
		lUserFriendReq = await sqlplus.list(UserFriendReq, [UserFriendReq.friend_user_id == user_id, ])
		req_user_id_list = [dUserFriendReq["req_user_id"] for dUserFriendReq in lUserFriendReq]
		lUser = await sqlplus.list(User, [User.id.in_(req_user_id_list), ])
		user_data_list = []
		for dUser in lUser:
			user_data_list.append({
				"id": dUser["id"],
				"grade": dUser["grade"],
				"fight": dUser["fight"],
				"level": dUser["level"],
				"user_name": dUser["user_name"],
				"icon": dUser["icon"],
			})
		await sender_user.send_refresh_user_friend_req(user_id, user_data_list)
	
	async def get_find_list(self, user_id, data):
		user_name = data["user_name"]
		lUser = await sqlplus.list(User, [User.user_name.like(f'%{user_name}%'), User.id != user_id], limit_count=10)
		friend_id_list = misc.to_one_dict("id", lUser)
		lUserFriend = await sqlplus.list(UserFriend, [UserFriend.user_id == user_id, UserFriend.friend_user_id.in_(friend_id_list) ], is_normal=False)
		user_friend_dict = misc.to_one_dict("friend_user_id",lUserFriend)
		
		user_data_list = []
		for dUser in lUser:
			dUserFriend = user_friend_dict.get(dUser["id"] ,None)
			if dUserFriend is not None:
				continue
			user_data_list.append({
				"id": dUser["id"],
				"grade": dUser["grade"],
				"fight": dUser["fight"],
				"level": dUser["level"],
				"user_name": dUser["user_name"],
				"icon": dUser["icon"],
			})
		await sender_user.send_refresh_find_user(user_id, user_data_list)
	
	async def get_user_data(self, user_id, data):
		dUser = await UserMgr.getObj().getUser(user_id)
		await sender_user.send_refresh_user(user_id, dUser)
	
	async def get_user_email(self, user_id, data):
		lUserEmail = await sqlplus.list(UserEmail, [UserEmail.user_id == user_id, ])
		await sender_user.send_refresh_email(user_id, misc.to_one_dict("id", lUserEmail))
	
	async def read_email(self, user_id, data):
		user_email_id = data["user_email_id"]
		
		await sqlplus.update(UserEmail, {
			"is_read": 1,
		}, [UserEmail.id == user_email_id, ])
		await sender_user.send_update_user_email_attr(user_id, user_email_id, "is_read", 1)
	
	@db.transaction()
	async def get_email_reward(self, user_id, data):
		
		user_email_id = data["user_email_id"]
		dUserEmail = await sqlplus.getOne(UserEmail, [UserEmail.id == user_email_id, ])
		if dUserEmail is None:
			await misc_logic.send_tip(user_id, "邮件不存在")
			return
		if dUserEmail["is_get"] == defines.FLAG_YES:
			await misc_logic.send_tip(user_id, "邮件已获取")
			return
		item_dict_list = json.loads(dUserEmail["item_json"])
		
		await sqlplus.update(UserEmail, {
			"is_get": 1,
		}, [UserEmail.id == user_email_id, ])
		
		await misc_logic.add_item_list_play_anim(user_id, item_dict_list)
		await sender_user.send_update_user_email_attr(user_id, user_email_id, "is_get", 1)
	
	async def del_email(self, user_id, data):
		user_email_id = data["user_email_id"]
		dUserEmail = await sqlplus.getOne(UserEmail, [UserEmail.id == user_email_id, ])
		if dUserEmail is None:
			return
		if dUserEmail["is_get"] == defines.FLAG_NO:
			await misc_logic.send_tip(user_id, "请先领取奖励")
			return
		await sqlplus.delete(UserEmail, [UserEmail.id == user_email_id, ])
		await sender_user.send_del_user_email(user_id, user_email_id)
	
	async def add_email(self, user_id, data):
		await sqlplus.insert(UserEmail, data)
		await sender_user.send_add_user_email(user_id, data)
	
	async def get_grade_rank(self, user_id, data):
		lUser = await sqlplus.list(User, order=[User.grade.desc(), ], limit_count=20)
		await sender_user.send_grade_rank(user_id, lUser)
	
	async def get_fight_rank(self, user_id, data):
		lUser = await sqlplus.list(User, order=[User.fight.desc(), ], limit_count=20)
		await sender_user.send_fight_rank(user_id, lUser)
