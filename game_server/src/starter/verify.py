#coding=utf-8
from fastapi import Request

import misc
from utils import auth_util


async def verify_token(request: Request):
	"""登录状态及权限校验依赖项"""
	if request.url.path.startswith("/noauth"):
		return

	token = request.headers.get('Authorization', '')
	request.user_id = auth_util.get_user_id(token)

	