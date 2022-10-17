import argparse
from asyncio.log import logger
import sys
import time
from typing import List, Tuple

import requests
from rich.console import Console
from rich.table import Table

from call_browser import call_browser
from config import Config as C
from login import login_ehall

LC = C.Table.LectureColumns


def fetch_lecture_list(session: requests.Session) -> Tuple[List, int]:
    res = session.get(C.URLs.lecture_list)
    lectures = res.json()["datas"]
    available_lectures = 0  # 可用讲座数量
    # 过滤多余内容
    for lecture in lectures:
        # 清理多余文字
        lecture[LC.Type.value] = lecture[LC.Type.value].replace("人文与科学素养系列讲座_", "")
        lecture[LC.Name.value] = str(lecture[LC.Name.value]).split("】", maxsplit=1)[1]
        # 转换格式
        seats = int(lecture[LC.SeatNum()])
        # 去掉年和秒
        lecture[LC.ReserveTime.value] = lecture[LC.ReserveTime.value][5:-3]
        lecture[LC.LectureTime.value] = lecture[LC.LectureTime.value][5:-3]
        if lecture[LC.Status.value] == 0:
            lecture[LC.Status.value] = C.LectureStatus.Lock
            lecture[LC.PersonNum.value] = lecture[LC.SeatNum()]  # str
        else:
            if lecture[LC.ReserveNum()] < seats:
                lecture[LC.Status.value] = C.LectureStatus.Vacancy
                available_lectures += 1
            else:
                lecture[LC.Status.value] = C.LectureStatus.Full
            lecture[LC.PersonNum.value] = f"{lecture[LC.ReserveNum()]}/{seats}"
    return lectures, available_lectures


def render_table(lectures: List):
    # 没有讲座时直接返回
    if len(lectures) == 0:
        C.logger.info("❌ No lecture found.")
        return
    C.logger.info(f"💖 Found {len(lectures)} lecture" + ["s.", "."][len(lectures) == 1])
    # 渲染讲座
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    # 表头
    for column in C.Table.columns_name:
        table.add_column(column, justify="center")
    # 讲座
    for lecture in lectures:
        C.logger.debug(lecture)
        status = lecture[LC.Status.value]
        props = (lecture[lc] for lc in C.Table.LectureColumns.values()[1:])
        table.add_row(status.value, *props, style=status.color())

    console.print(table)
    console.print(
        "[dim i][bold]Link of Lectures:[/bold][/dim i]\n",
        f"   [dim i]{C.URLs.lecture_page}[/dim i]",
    )


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="SEU Lecture Monitor",
        description="获取东南大学讲座列表.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-r",
        "--repeat",
        dest="repeat",
        action="store_true",
        help="定时获取讲座列表. 当发现有可用讲座时, 启动浏览器.",
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
    return parser.parse_args()


def repeat(times: int, interval: int, session: requests.Session):
    for i in range(times):
        if i:  # sleep when i > 0
            time.sleep(interval)
        lectures, available_lectures = fetch_lecture_list(session=session)
        C.logger.info(
            "发现 %s 个讲座, 其中 %s 个可用. (第 %s/%s 次检查)",
            len(lectures),
            available_lectures,
            i + 1,
            times,
        )
        if available_lectures:
            call_browser()
            return


if __name__ == "__main__":
    args = get_args()
    C.logger.debug(f"{args=}")

    session, student_name = login_ehall(C.username, C.password)
    if not student_name:
        C.logger.error("❌Login failed. Cannot get student name.")
        sys.exit(1)

    C.logger.info(f"✨ {'***' if C.privacy_mode else student_name}, Welcome! ✨")
    if args.repeat:
        try:
            repeat(args.times, args.interval, session)
        except KeyboardInterrupt:
            logger.info("Terminated by user.")
    else:
        lectures, available_lectures = fetch_lecture_list(session=session)
        render_table(lectures)
