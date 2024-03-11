#coding=utf-8
import hashlib
import time

import jwt

import setting
from base.base import AppException
from base.http_base import HttpResp


def generate_token(payload):
	payload['exp'] = int(time.time()) + setting.TOKEN_TIME
	token = jwt.encode(payload, setting.TOKEN_SECRET, algorithm='HS256')
	return token


def get_user_id(token):
	payload = jwt.decode(token, setting.TOKEN_SECRET, algorithms='HS256')
	exp = int(payload.pop('exp'))
	if time.time() > exp:
		raise AppException(HttpResp.FAILED, msg='token失效!')
	return payload["user_id"]

def md5(password):
	# md5
	md5 = hashlib.md5()
	# 转码
	sign_utf8 = str(password).encode(encoding="utf-8")
	# 加密
	md5.update(sign_utf8)
	# 返回密文
	return md5.hexdigest()