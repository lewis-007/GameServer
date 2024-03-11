# coding=utf-8
import builtins
import logging


import global_var

old_print = print

from functools import partial


def my_print(*args, **kwargs):
	old_print(*args, **kwargs)
	sep = kwargs.get('sep', ' ')
	try:
		text = sep.join(args)
		global_var.logger.info(text)
	except:
		pass


def replace_print():
	builtins.print = partial(my_print, sep=' ', end='\n')


def init_logger():
	replace_print()
	logging.basicConfig(level=logging.INFO,
	                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s',
	                    datefmt='%Y-%m-%d %H:%M:%S',
	                    filename='info.log')
	# handler = RotatingFileHandler('info.log', maxBytes=1024 * 1024, backupCount=5)  # 设置日志文件大小为1MB，最多保留5个备份文件
	# handler.terminator = ""
	#
	# # 第三步：添加控制台文本处理器
	# console_handler = logging.StreamHandler()
	# console_handler.terminator = ""
	# console_handler.setLevel(level=logging.INFO)
	# console_fmt = "%(asctime)s - %(levelname)s - %(message)s"
	# fmt1 = logging.Formatter(fmt=console_fmt)
	# console_handler.setFormatter(fmt=fmt1)
	#
	logger = logging.getLogger(__name__)

	
	global_var.logger = logger
