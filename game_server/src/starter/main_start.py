#coding=utf-8
import datetime
import json
import logging
import pprint

from fastapi import Depends
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic.error_wrappers import ValidationError

from pymysql import OperationalError
from sqlalchemy.sql import TableClause
from starlette.exceptions import HTTPException as StarletteHTTPException



from base.base import AppException
from base.http_base import HttpResp

from base import http_base
from entity.common import UserItem
from sql import sqlplus
from starter import verify

logger = logging.getLogger(__name__)


def create_app():
	configure_json()
	
	app = FastAPI()
	
	configure_exception(app)
	configure_event(app)
	configure_middleware(app)
	

	configure_router(app)
	return app


# 配置中间件
def configure_middleware(app: FastAPI):
	from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
	from starter.middlewares import init_cors_middleware, init_timeout_middleware
	
	app.add_middleware(ProxyHeadersMiddleware)
	init_cors_middleware(app)
	init_timeout_middleware(app)


def configure_json():
	class DateEncoder(json.JSONEncoder):
		def default(self, obj):
			if isinstance(obj, datetime.datetime):
				
				return obj.strftime("%Y-%m-%d %H:%M:%S")
			else:
				return json.JSONEncoder.default(self, obj)
	
	json._default_encoder = DateEncoder(
		skipkeys=False,
		ensure_ascii=True,
		check_circular=True,
		allow_nan=True,
		indent=None,
		separators=None,
		default=None,
	)


# 启动后的连接数据库
def configure_event(app: FastAPI):
	from sql.database import db
	@app.on_event('startup')
	async def startup():
		await db.connect()
		import mgr.timer_mgr as timer_mgr
		await timer_mgr.startTimer()


	
	@app.on_event('shutdown')
	async def shutdown():
		await db.disconnect()


# 配置路由
def configure_router(app: FastAPI):
	from api import noauth
	from api import test
	from server_module import server
	admin_deps = [Depends(verify.verify_token)]
	app.include_router(server.router, dependencies=admin_deps)
	app.include_router(noauth.router, dependencies=admin_deps)
	app.include_router(test.router, dependencies=admin_deps)


# 配置全局异常处理
def configure_exception(app: FastAPI):
	@app.exception_handler(RequestValidationError)
	async def validation_exception_handler(request: Request, exc: RequestValidationError):
		"""处理请求参数验证的异常
			code: 310 311
		"""
		resp = http_base.HttpResp.PARAMS_VALID_ERROR
		errs = exc.errors()
		if errs and errs[0].get('type', '').startswith('type_error.'):
			resp = HttpResp.PARAMS_TYPE_ERROR
		logger.warning('validation_exception_handler: url=[%s], errs=[%s]', request.url.path, errs)
		return JSONResponse(
			status_code=resp.code,
			content={'code': resp.code, 'msg': resp.msg, 'data': errs})
	
	@app.exception_handler(StarletteHTTPException)
	async def http_exception_handler(request: Request, exc: StarletteHTTPException):
		"""处理客户端请求异常
			code: 312 404
		"""
		logger.error(exc, exc_info=True)
		logger.warning('http_exception_handler: url=[%s], status_code=[%s]', request.url.path, exc.status_code)
		resp = HttpResp.SYSTEM_ERROR
		if exc.status_code == 404:
			resp = HttpResp.REQUEST_404_ERROR
		elif exc.status_code == 405:
			resp = HttpResp.REQUEST_METHOD_ERROR
		return JSONResponse(
			status_code=resp.code,
			content={'code': resp.code, 'msg': resp.msg, 'data': []})
	
	@app.exception_handler(AssertionError)
	async def assert_exception_handler(request: Request, exc: AssertionError):
		"""处理断言异常
			code: 313
		"""
		errs = ','.join(exc.args) if exc.args else HttpResp.ASSERT_ARGUMENT_ERROR.msg
		logger.warning('app_exception_handler: url=[%s], errs=[%s]', request.url.path, errs)
		return JSONResponse(
			status_code=HttpResp.ASSERT_ARGUMENT_ERROR.code,
			content={'code': HttpResp.ASSERT_ARGUMENT_ERROR.code, 'msg': errs,
			         'data': []})
	
	@app.exception_handler(AppException)
	async def app_exception_handler(request: Request, exc: AppException):
		"""处理自定义异常
			code: .
		"""
		if exc.echo_exc:
			logger.error('app_exception_handler: url=[%s]', request.url.path)
			logger.error(exc, exc_info=True)
		return JSONResponse(
			status_code=exc.code,
			content={'code': exc.code, 'msg': exc.msg, 'data': []})
	
	@app.exception_handler(ValidationError)
	async def validation_exception_handler(request: Request, exc: ValidationError):
		"""处理参数验证的异常 (除请求参数验证之外的)
			code: 500
		"""
		logger.error('validation_exception_handler: url=[%s]', request.url.path)
		logger.error(exc, exc_info=True)
		return JSONResponse(
			status_code=HttpResp.SYSTEM_ERROR.code,
			content={'code': HttpResp.SYSTEM_ERROR.code, 'msg': HttpResp.SYSTEM_ERROR.msg, 'data': []})
	
	@app.exception_handler(OperationalError)
	async def db_opr_error_handler(request: Request, exc: OperationalError):
		"""处理连接异常
			code: 500
		"""
		from sql.database import db
		logger.error('db_opr_error_handler: url=[%s]', request.url.path)
		logger.error(exc, exc_info=True)
		await db._backend._pool.clear()
		return JSONResponse(
			status_code=HttpResp.SYSTEM_ERROR.code,
			content={'code': HttpResp.SYSTEM_ERROR.code, 'msg': HttpResp.SYSTEM_ERROR.msg, 'data': []})
	
	@app.exception_handler(Exception)
	async def global_exception_handler(request: Request, exc: Exception):
		"""处理服务端异常, 全局异常处理
			code: 500
		"""
		logger.error('global_exception_handler: url=[%s]', request.url.path)
		logger.error(exc, exc_info=True)
		return JSONResponse(
			status_code=HttpResp.SYSTEM_ERROR.code,
			content={'code': HttpResp.SYSTEM_ERROR.code, 'msg': HttpResp.SYSTEM_ERROR.msg, 'data': []})
