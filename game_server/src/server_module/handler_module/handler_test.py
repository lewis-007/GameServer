#coding=utf-8

import misc
from base.singleton import SingletonBase
from entity.common import User
from mgr.user_mgr import UserMgr
from server_module import misc_logic
from server_module.handler_module.handler_user import HandleUser
from server_module.logic.logic_item import LogicItem
from server_module.sender import sender_user
from sql import sqlplus


async def handle(data: dict):
	obj = HandleTest.getObj()
	await getattr(obj, data["func"])(data["user_id"], data)


class HandleTest(SingletonBase):
	async def test_add_exp(self, user_id, data):
		await misc_logic.update_user_attr(user_id, "level", 1)
		#await misc_logic.add_user_exp(user_id, 170+241)
	
	async def test_down_item(self, user_id, data):
		await misc_logic.down_item(user_id, 4,10)

	async def test_add_email(self, user_id, data):
		await HandleUser.getObj().add_email(user_id, {
			"user_id": user_id,
			"item_json": '[{"item_num": 1, "item_amount": 10}]',
			"email_title": "测试添加",
			"email_content": "内容不重要",
			"is_read": 0,
			"is_get": 0
		})

	async def test_add_item_list(self, user_id, data):

		item_dict_list = [
			{
				"item_num": 1007,
				"item_amount": 1,
			},
			{
				"item_num": 2,
				"item_amount": 2,
			},
			{
				"item_num": 1,
				"item_amount": 2,
			},
			{
				"item_num": 4,
				"item_amount": 10,
			},
		]

		await misc_logic.add_item_list_play_anim(user_id, item_dict_list)