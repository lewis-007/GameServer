#coding=utf-8
from common import defines


def is_str_num(s):
	return s.isnumeric()
	
def is_long(num):
	return num > defines.LONG_MXA or num < defines.LONG_MIN

def to_json_dict(data_dict):
	result = {}
	for key in data_dict:
		value = data_dict[key]
		if type(value) is list:
			result[key] = to_json_list(value)
		elif type(value) is dict:
			result[key] = to_json_dict(value)
		elif type(value) is int and is_long(value):
			result[key] = str(value)
		else:
			result[key] = value
	return result

def to_json_list(lst):
	result_lst = []
	for value in lst:
		if type(value) is list:
			result_lst.append(to_json_list(value))
		elif type(value) is dict:
			result_lst.append(to_json_dict(value))
		elif type(value) is int and is_long(value):
			result_lst.append(str(value))
		else:
			result_lst.append(value)
	return result_lst

def from_json_dict(data_dict):
	result = {}
	for key in data_dict:
		value = data_dict[key]
		if type(value) is list:
			result[key] = from_json_list(value)
		elif type(value) is dict:
			result[key] = from_json_dict(value)
		elif type(value) is str and is_str_num(value) and is_long(int(value)):
			result[key] = int(value)
		else:
			result[key] = value
	return result

def from_json_list(lst):
	result_lst = []
	for value in lst:
		if type(value) is list:
			result_lst.append(from_json_list(value))
		elif type(value) is dict:
			result_lst.append(from_json_dict(value))
		elif type(value) is str and is_str_num(value) and is_long(int(value)):
			result_lst.append(int(value))
		else:
			result_lst.append(value)
	return result_lst