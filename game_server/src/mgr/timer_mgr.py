# coding=utf-8
import asyncio

from apscheduler.schedulers.background import BackgroundScheduler
import misc
from base import functor
from base.singleton import SingletonBase
from entity.common import User

from sql import sqlplus
import schedule


async def startTimer():
	await TimerMgr.getObj().startLoop()


# 凌晨执行
def day_task():
	loop = asyncio.get_event_loop()
	from server_module.logic.logic_common import LogicCommon
	loop.run_until_complete(LogicCommon.getObj().day_refresh_user_login())  # 重置用户日首次登录


# 月初执行
def month_task():
	loop = asyncio.get_event_loop()
	from server_module.logic.logic_common import LogicCommon
	loop.run_until_complete(LogicCommon.getObj().month_refresh_user_login())  # 重置用户月首次登录


class TimerMgr(SingletonBase):
	def __init__(self):
		self.time_dict = {}
		self.time_add = 0
	
	async def startLoop(self):
		asyncio.ensure_future(self.loop())
		# 设置定时任务为每天凌晨1点执行
		schedule.every().day.at("00:00").do(day_task)
		#schedule.every().day.at("20:00").do(month_task)
		schedule.every().monday.do(month_task)
	
	def addTimer(self, obj, func_name, dt, isLoop=False, *args):
		callTime = self.time_add + dt
		
		obj_dict = self.time_dict.get(callTime, None)
		if obj_dict is None:
			obj_dict = {}
			self.time_dict[callTime] = obj_dict
		func_obj_list = obj_dict.get(obj, None)
		if func_obj_list is None:
			func_obj_list = []
			obj_dict[obj] = func_obj_list
		func_obj_list.append({
			"isLoop": isLoop,
			"func_name": func_name,
			"dt": dt,
			"args": args
		})
	
	async def runTimer(self):
		nowTime = self.time_add
		obj_dict = self.time_dict.get(nowTime, None)
		if obj_dict is None:
			return
		
		for obj in obj_dict:
			func_obj_list = obj_dict.get(obj, None)
			if func_obj_list is None:
				continue
			for func_obj in func_obj_list:
				await self.runFunc(obj, func_obj)
		
		self.time_dict.pop(nowTime, None)
	
	async def runFunc(self, obj, func_obj):
		if func_obj["args"] is not None and len(func_obj["args"]) > 0:
			await functor.Functor(obj, func_obj["func_name"])(func_obj["args"])
		else:
			await functor.Functor(obj, func_obj["func_name"])()
		
		if func_obj["isLoop"]:
			if func_obj["args"] is not None and len(func_obj["args"]) > 0:
				self.addTimer(obj, func_obj["func_name"], func_obj["dt"], func_obj["isLoop"], *func_obj["args"])
			else:
				self.addTimer(obj, func_obj["func_name"], func_obj["dt"], func_obj["isLoop"])
	
	async def loop(self):
		while True:
			await asyncio.sleep(1)
			await self.runTimer()
			schedule.run_pending()
			self.time_add += 1
