# coding=utf-8


TOKEN_SECRET = "zhl"  # token加密密匙
TOKEN_TIME = 3600 * 24 * 3  # token时效3天

MYSQL_USER = "root"  # 数据库用户名
MYSQL_PWD = "root"  # 数据库密码
MYSQL_HOST = "127.0.0.1"  # 数据库ip
MYSQL_POST = 3306  # 数据库端口
MYSQL_DB_NAME = "game_server"  # 数据库名称

SERVER_IP = "127.0.0.1"  # 服务器ip
SERVER_PORT = 8000  # 服务器端口

RELOAD = True  # 是否使用热重载


def init_config():
	import json
	
	with open('../config.json', 'r') as f:
		content = f.read()
		config_dict = json.loads(content)
		for key in config_dict:
			value = globals().get(key, None)
			
			if value is None:
				continue
			globals()[key] = config_dict[key]
