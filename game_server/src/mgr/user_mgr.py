# coding=utf-8

import misc
from base.singleton import SingletonBase
from entity.common import User
from mgr.timer_mgr import TimerMgr


class UserMgr(SingletonBase):
	def __init__(self):
		self.user_dict = {}
		self.heart_set = set()
		TimerMgr.getObj().addTimer(self, "loop", 15, True)
	
	async def loop(self):
		await self.checkHeart()
	
	async def addUser(self, dUser: dict):
		self.heart_set.add(dUser["id"])
		self.user_dict[dUser["id"]] = dUser
	
	async def removeUser(self, user_id):
		self.user_dict.pop(user_id, None)
	
	async def getUser(self, user_id) -> dict:
		return self.user_dict.get(user_id, None)
	
	async def heartUser(self, user_id):
		self.heart_set.add(user_id)
	
	async def checkHeart(self):
		closeSet = set()
		for user_id in self.user_dict:
			if user_id in self.heart_set:
				continue
			closeSet.add(user_id)
		
		for user_id in closeSet:
			print("心跳超时",user_id)
			await misc.close_user(user_id)
		self.heart_set = set()
