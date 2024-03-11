# coding=utf-8
import inspect
import json
import traceback

import global_var
from base.singleton import SingletonBase
from common import defines

from server_module.handler_module import handler_common, handler_user, handler_hero, handler_item, handler_test, \
	handler_fight

from utils import proto_util

g_msg_list = []

def delay_send(func):
	async def wrapper(*args, **kwargs):
		from server_module.server import ConnMgr
		global g_msg_list
		resp = None
		try:
			if inspect.iscoroutinefunction(func):
				resp = await func(*args, **kwargs)
			else:
				resp = func(*args, **kwargs)
		except:
			traceback.print_exc()
			g_msg_list = []
			
		
		for data_tutle in g_msg_list:
			try:
				data_dict = data_tutle[1]
				await ConnMgr.getObj().send_data(data_tutle[0], json.dumps(data_dict))
			except:
				print("协议发送异常 ",data_tutle)
		g_msg_list = []
		return resp
	return wrapper

async def handle_msg(user_id, msg: str):
	await HandlerMgr.getObj().handle_msg(user_id, msg)


class HandlerMgr(SingletonBase):
	def __init__(self):
		self.handler_module = {}
		self.init()
	
	def init(self):
		self.handler_module[defines.C2S_COMMON] = handler_common
		self.handler_module[defines.C2S_USER] = handler_user
		self.handler_module[defines.C2S_HERO] = handler_hero
		self.handler_module[defines.C2S_ITEM] = handler_item
		self.handler_module[defines.C2S_FIGHT] = handler_fight
		self.handler_module[defines.C2S_TEST] = handler_test
		
	
	@delay_send
	async def handle_msg(self, user_id: int, msg: str):
		data = json.loads(msg)
		data["user_id"] = user_id
		print("recv ", data["type"], data["func"])
		await self.handler_module[data["type"]].handle(proto_util.from_json_dict(data))
		
