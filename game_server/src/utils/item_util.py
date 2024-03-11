# coding=utf-8
from common import defines
from data import RuneData


def check_is_rune_item(item_num):
	if item_num < defines.OFFSET_RUNE2ITEM:
		return False
	if item_num >= defines.OFFSET_RUNE2ITEM + len(RuneData.data.keys()):
		return False
	
	return True
