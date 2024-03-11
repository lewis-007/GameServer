#coding=utf-8
import hashlib
import math
import time

import jwt

import setting
from base.base import AppException
from base.http_base import HttpResp
from data import HeroData, GameSettingData


def calAttr(hero_num, hero_grade, key:str):

	heroData = HeroData.data.get(hero_num)
	
	data = GameSettingData.data.get(0)
	
	firstUpKey = key[0].upper() + key[1:]
	return math.floor(heroData[key] * hero_grade * data["hero" + firstUpKey + "Radio"] + heroData[key])



def calAdventureSilver(level):
	data = GameSettingData.data.get(0)
	return int(data["adventureSilverStartNum"] + data["adventureSilverRadio"] * level)



def calAdventureReward(level):
	data = GameSettingData.data.get(0)
	return int(data["adventureRewardStartNum"] + data["adventureRewardRadio"] * level)


def calUserLevelExp(level):
	data = GameSettingData.data.get(0)
	return int(data["adventureExpStartNum"] + data["adventureExpRadio"] * level)
