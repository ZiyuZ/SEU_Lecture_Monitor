import logging
import sys
from pathlib import Path

from environs import Env
from rich.logging import RichHandler

# init logger
logging.basicConfig(
    level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger("rich")

if not Path("./.env").exists():
    logger.error(
        'File ".env" not found. Please rename ".env.example" to ".env" and edit it.'
    )
    sys.exit(1)

# read .env file
env = Env()
env.read_env()


class Config:
    username = env("SEU_USERNAME")
    password = env("SEU_PASSWORD")
    logger = logger

    encrypt_js = "./src/ids-encrypt.js"
    privacy_mode = False  # set False to display personal information

    class URLs:
        login_page = "https://newids.seu.edu.cn/authserver/login"
        lecture_page = "http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/*default/index.do"
        lecture_list = (
            "http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/hdyy/queryActivityList.do"
        )

    class Table:
        columns = [
            "状态",
            "人数",
            ":coffee: 名称",
            ":school: 地点",
            ":pencil: 类型",
            ":alarm_clock: 预约开始时间",
            ":date: 活动时间",
            # ":studio_microphone: 主讲人",
        ]

        lecture_column = [
            "SFKSYY",
            "YYRS_HDZRS",
            "JZMC",
            "JZDD",
            "JZXL_DISPLAY",
            "YYKSSJ",
            "JZSJ",
            # "ZJR",
        ]
