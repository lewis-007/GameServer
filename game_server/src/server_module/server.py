#coding=utf-8
import json

from fastapi import APIRouter
from starlette.endpoints import WebSocketEndpoint

import misc
from base.singleton import SingletonBase
from common import defines
from entity.common import User
from mgr.user_mgr import UserMgr
from server_module import handler
from sql import sqlplus
from utils import auth_util

router = APIRouter(prefix='/ws')



@router.websocket_route("/ws/{user_id}", name="ws")
class Conn(WebSocketEndpoint):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.user_id = args[0]['path_params'].get('user_id')
		# self.token = args[0]['path_params'].get('token')
		# self.user_id = auth_util.get_user_id(self.token)  # token校验
		self.websocket = None
	
	# 开始有链接上来的时候对应的处理
	async def on_connect(self, websocket):
		self.websocket = websocket
		await websocket.accept()
		await ConnMgr.getObj().add_conn(self)
	
	# 客户端开始有数据发送过来的时候的处理
	async def on_receive(self, websocket, data):
		await ConnMgr.getObj().recv_data(self.user_id, data)
	
	# 客户端断开链接的时候
	async def on_disconnect(self, websocket, close_code):
		# 进行全局的广播所有的在线链接的所有用户消息
		try:
			print("客户端断开连接")
			await misc.close_user(self.user_id)
		except:
			# 倒计时自动结束的之后，客户端再点击一次断开的时候异常处理！
			pass
	
	async def send_data(self, message: str):
		await self.websocket.send_text(message)
	
	async def close_conn(self):
		await self.websocket.close()


class ConnMgr(SingletonBase):
	def __init__(self):
		self.conn_dict: [int, Conn] = {}
	
	async def connSucc(self, user_id):
		dUser = await sqlplus.getOne(User, [User.id == user_id, ])
		if dUser is None:
			await misc.close_user(user_id)
			return
		await UserMgr.getObj().addUser(dUser)
		await self.send_data(user_id, json.dumps({
			"type": defines.S2C_COMMON,
			"func": "connSucc",
		}))

	
	async def add_conn(self, conn):
		old_conn = self.conn_dict.get(conn.user_id, None)
		if old_conn is not None:
			await self.close_conn(old_conn.user_id)
			print(f"用户 {old_conn.user_id} 被顶号")
		self.conn_dict[conn.user_id] = conn
		print(f"用户 {conn.user_id} 上线，在线人数：{len(self.conn_dict)}")
		await self.connSucc(conn.user_id)
	
	async def recv_data(self, user_id, msg: str):
		conn = self.conn_dict[user_id]
		if conn is None:
			return
		await handler.handle_msg(user_id, msg)
	
	async def send_data(self, user_id, msg: str):
		conn = self.conn_dict[user_id]
		if conn is None:
			return
		await conn.send_data(msg)
	
	async def remove_conn(self, user_id):
		await self.close_conn(user_id)
		
	
	async def close_conn(self, user_id):
		conn = self.conn_dict.pop(user_id, None)
		print(f"用户 {user_id} 下线，在线人数：{len(self.conn_dict)}")
		if conn is None:
			return
		try:
			await conn.close_conn()
		except:
			pass
