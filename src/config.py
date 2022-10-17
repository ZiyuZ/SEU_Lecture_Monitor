import logging
import sys
from enum import Enum
from pathlib import Path

from environs import Env
from rich.logging import RichHandler

# read .env file
# env.read_env() will be empty if no .env file
env = Env()
env.read_env()
log_level = env("LOG_LEVEL", "DEBUG")  # set log level even no .env file
# init logger
logging.basicConfig(
    level=log_level, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger("rich")

# check .env file
if not Path("./.env").exists():
    logger.error(
        'File ".env" not found. Please rename ".env.example" to ".env" and edit it.'
    )
    sys.exit(1)


class Config:
    username = env("SEU_USERNAME")
    password = env("SEU_PASSWORD")
    logger = logger

    encrypt_js = "./src/ids-encrypt.js"
    # set False to display personal information
    privacy_mode = env("PRIVACY_MODE") == "1"

    class URLs:
        login_page = "https://newids.seu.edu.cn/authserver/login"
        lecture_page = "http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/*default/index.do"
        lecture_list = (
            "http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/hdyy/queryActivityList.do"
        )

    class LectureStatus(Enum):
        Lock = "🔒"
        Full = "🛑"
        Vacancy = "✅"

        def color(self):
            return {
                # self.Lock: "#b3b3b3",
                self.Vacancy: "#9cff2f",
                self.Full: "#fa1740",
            }.get(self)

    class Table:
        columns_name = [
            "📌",
            "👥 人数",
            "🔖 名称",
            "🏫 地点",
            "📝 类型",
            "⏰ 预约时间",
            "📅 活动时间",
            # ":studio_microphone: 主讲人",
        ]

        class LectureColumns(Enum):
            Status = "SFKSYY"  # 是否开始预约
            PersonNum = "YYRS_HDZRS"  # 预约人数/活动总人数
            Name = "JZMC"  # 讲座名称
            Place = "JZDD"  # 讲座地点
            Type = "JZXL_DISPLAY"  # 讲座系列
            ReserveTime = "YYKSSJ"  # 预约开始时间
            LectureTime = "JZSJ"  # 讲座时间
            # Presenter =  "ZJR" # 主讲人

            @classmethod
            def values(cls):
                return [v.value for v in cls.__members__.values()]

            @classmethod
            def ReserveNum(cls):
                return "YYRS"

            @classmethod
            def SeatNum(cls):
                return "HDZRS"
