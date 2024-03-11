# coding=utf-8
import datetime
import time

import misc
from base.singleton import SingletonBase
from entity.common import User
from entity.fight_enetity import Team, FightRoom, ReadyRoom
from mgr.timer_mgr import TimerMgr


class ReadyRoomMgr(SingletonBase):
	def __init__(self):
		self.room_dict = {}
		#TimerMgr.getObj().addTimer(self, "loop", 28, True)
	
	async def loop(self):
		now_time = int(time.time())
		remove_list = []
		for user_id in self.room_dict:
			ready_room = self.room_dict[user_id]
			if now_time - ready_room.time>60:#1分钟
				remove_list.append(user_id)
		
		for user_id in remove_list:
			await self.removeReadyRoom(user_id)
			
	async def addReadyRoom(self, user_id0: int):
		ready_room = ReadyRoom()
		ready_room.user_id0 = user_id0
		ready_room.time = int(time.time())
		
		self.room_dict[user_id0] = ready_room
		print("当前准备房间数：" , len(self.room_dict))
	
	async def removeReadyRoom(self, user_id):
		self.room_dict.pop(user_id, None)
		print("剩余准备房间数：" , len(self.room_dict))
	
	async def getReadyRoom(self, user_id) -> ReadyRoom:
		return self.room_dict.get(user_id, None)
	
	async def getCanStartRoom(self)-> ReadyRoom:
		if len(self.room_dict) == 0:
			return None
		return list(self.room_dict.values())[0]
	
