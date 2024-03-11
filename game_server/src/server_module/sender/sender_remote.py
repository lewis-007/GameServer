# coding=utf-8
import requests

async def send_fight_result(user_id0,user_id1,win_user_id):
	datas = {"userId0": user_id0, "userId1": user_id1, "winUserId": win_user_id}
	requests.post("https://testapp.xfx.hk/game/gameEnd", data=datas)

