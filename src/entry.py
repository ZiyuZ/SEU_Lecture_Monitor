import argparse
import sys

from config import Config as C
from lecture import LectureList
from utils import call_browser, login_ehall


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="SEU Lecture Monitor",
        description="获取东南大学讲座列表. 不带任何参数时, 获取并打印讲座列表.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-a",
        "--all",
        dest="with_disabled",
        action="store_true",
        help="打印所有讲座, 包含已经取消的活动.",
    )
    parser.add_argument(
        "-r",
        "--repeat",
        dest="repeat",
        action="store_true",
        help="定时获取讲座列表. 当发现有可用讲座时, 启动浏览器. 该参数隐含了 --browser.",
    )
    parser.add_argument(
        "-i",
        "--interval",
        dest="interval",
        type=int,
        default=60,
        nargs="?",
        help="定时获取讲座的尝试时间间隔, 在使用参数 '-r' 后生效. 单位: 秒.",
    )
    parser.add_argument(
        "-t",
        "--times",
        dest="times",
        type=int,
        default=3,
        nargs="?",
        help="定时获取讲座的尝试次数, 在使用参数 '-r' 后生效.",
    )
    parser.add_argument(
        "-b",
        "--browser",
        dest="browser",
        action="store_true",
        help="打开讲座列表网页.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="调试模式.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    if args.debug:
        C.logger.setLevel("DEBUG")
    C.logger.debug(f"{args=}")
    if args.browser and not args.repeat:
        C.logger.info("Call browser.")
        call_browser()
        sys.exit(0)

    session, student_name = login_ehall(C.username, C.password)
    if not student_name:
        C.logger.error("❌ Login failed. Cannot get student name.")
        sys.exit(1)

    C.logger.info(f"✨ {'***' if C.privacy_mode else student_name}, Welcome! ✨")
    lectures = LectureList(session=session)
    if args.repeat:
        try:
            if lectures.check_vacant(times=args.times, interval=args.interval):
                call_browser()
        except KeyboardInterrupt:
            C.logger.info("Terminated by user.")
    else:
        lectures.fetch()
        lectures.render_table(lectures, with_disabled=args.with_disabled)
