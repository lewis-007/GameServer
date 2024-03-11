#coding=utf-8

from fastapi import APIRouter, Request
from base.http_base import unified_resp

router = APIRouter(prefix='/test')



@router.post('/test')
@unified_resp
async def test(params: dict,request: Request):
	print(f"AAAAAAA {request.user_id}")






