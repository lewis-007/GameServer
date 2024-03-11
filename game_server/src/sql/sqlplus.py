# coding=utf-8
from typing import List

import misc
from utils import datetime_util, id_util
from sql.database import db


def _to_cls_dict(cls, dict: dict):
	data = {}
	for key in dict:
		v = getattr(cls, key, None)
		if v is None:
			continue
		data[key] = dict[key]
	return data


async def insert(cls, data: dict, is_normal: bool = True):
	data["id"] = id_util.get_id()
	if is_normal:
		data["create_time"] = datetime_util.get_now_str()
		data["update_time"] = datetime_util.get_now_str()
	await db.execute(cls.__table__.insert().values(**_to_cls_dict(cls, data)))
	return data["id"]


async def insert_list(cls, lst: list, is_normal: bool = True):
	if misc.is_empty(lst):
		return
	if is_normal:
		for data in lst:
			data["create_time"] = datetime_util.get_now_str()
			data["update_time"] = datetime_util.get_now_str()
	data_list = []
	for data in lst:
		data["id"] = id_util.get_id()
		data_list.append(_to_cls_dict(cls, data))
	return await db.execute(cls.__table__.insert().values(lst))


async def update(cls, data: dict, where: list = None, is_normal: bool = True):
	if is_normal:
		data["update_time"] = datetime_util.get_now_str()
	if where:
		return await db.execute(cls.__table__.update().where(*where).values(**data))
	return await db.execute(cls.__table__.update().values(**data))


async def update_list(cls, lst: list, where: list = None, is_normal: bool = True):
	if misc.is_empty(lst):
		return
	if is_normal:
		for data in lst:
			data["update_time"] = datetime_util.get_now_str()
	
	if where:
		return await db.execute_many(cls.__table__.update().where(*where), lst)
	
	return await db.execute_many(str(cls.__table__.update()).replace("id=:id, ", "") + " WHERE id=:id", lst)


async def delete(cls, where: list = None, is_normal: bool = True):
	if is_normal:
		data = {
			"is_delete": 1,
			"delete_time": datetime_util.get_now_str()
		}
		if where:
			return await db.execute(cls.__table__.update().where(*where).values(**data))
		return await db.execute(cls.__table__.update().values(**data))
	return await db.execute(cls.__table__.delete().where(*where))


async def delete_list(cls, where: list = None, is_normal: bool = True):
	if is_normal:
		return await update_list(cls, [{'is_delete': 1, 'delete_time': datetime_util.get_now_str()}], where)


async def getOne(cls: object, where: list = None, is_normal: bool = True) -> dict:
	if where is None:
		where = []
	if is_normal:
		where.append(cls.is_delete == 0)
	obj = await db.fetch_one(cls.__table__.select().where(*where).limit(1))
	if obj is None:
		return None
	return dict(obj)


#
# async def page(cls, where: list = None, order: list = None, pageParams=PageParams()):
# 	if where is None:
# 		where = []
# 	where.append(cls.is_delete == 0)
#
# 	if where and order:
# 		return await paginate(db, cls.__table__.select().where(*where).order_by(*order), pageParams)
# 	return await paginate(db, cls.__table__.select().where(*where), pageParams)


async def list(cls, where: list = None, order: list = None, limit_count: int = None, is_normal: bool = True):
	if where is None:
		where = []
	if is_normal:
		where.append(cls.is_delete == 0)
	
	result = None
	op = cls.__table__.select()
	if where:
		op = op.where(*where)
	if order:
		op = op.order_by(*order)
	if limit_count:
		op = op.limit(limit_count)
	result = await db.fetch_all(op)
	if misc.is_empty(result):
		return []
	result = [dict(i) for i in result]
	return result
