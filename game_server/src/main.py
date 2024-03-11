# coding=utf-8
import log
log.init_logger()
print("------------------------------------------------------------------------------------------------------------------")

import setting
setting.init_config()

if __name__ == '__main__':
	import uvicorn

	uvicorn.run(app='main:app', host=setting.SERVER_IP, port=setting.SERVER_PORT, reload=setting.RELOAD)


from starter import main_start
app = main_start.create_app()

