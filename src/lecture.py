import argparse
import time
from typing import List, Tuple

import requests
from rich.console import Console
from rich.table import Table

from call_browser import call_browser
from config import Config as C
from login import login_ehall


def fetch_lecture_list(session: requests.Session) -> Tuple[List, int]:
    res = session.get(C.URLs.lecture_list)
    lectures = res.json()["datas"]
    available_lectures = 0  # 可用讲座数量
    # 过滤多余内容
    for lecture in lectures:
        lecture["JZXL_DISPLAY"] = lecture["JZXL_DISPLAY"].replace("人文与科学素养系列讲座_", "")
        lecture["HDZRS"] = int(lecture["HDZRS"])
        if lecture["SFKSYY"] == 0:
            lecture["SFKSYY"] = "🔒"  # "❌"
        elif lecture["YYRS"] < lecture["HDZRS"]:
            lecture["SFKSYY"] = "✔"
            available_lectures += 1
        else:
            lecture["SFKSYY"] = "🈵"
        lecture["YYRS_HDZRS"] = f'{lecture["YYRS"]}/{lecture["HDZRS"]}'
    return lectures, available_lectures


def render_table(lectures: List):
    # 没有讲座时直接返回
    if len(lectures) == 0:
        C.logger.info("❌ No lecture found.")
        return
    C.logger.info(f"💖 {len(lectures)} lecture(s) were found.")
    # 渲染讲座
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    for column in C.Table.columns:
        table.add_column(column, justify="center")
    for lecture in lectures[::-1]:
        table.add_row(*list(lecture[lc] for lc in C.Table.lecture_column))

    console.print(table)
    console.print(
        f"[dim i][bold]Link of Lectures:[/bold]\n   {C.URLs.lecture_page}[/dim i]"
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


if __name__ == "__main__":
    args = get_args()
    C.logger.debug(f"{args=}")

    session, student_name = login_ehall(C.username, C.password)
    if student_name:
        C.logger.info(f"✨ {'***' if C.privacy_mode else student_name}, Welcome! ✨")
        if args.repeat:
            for i in range(args.times):
                if i:  # sleep when i > 0
                    time.sleep(args.interval)
                lectures, available_lectures = fetch_lecture_list(session=session)
                C.logger.info(
                    f"发现 {len(lectures)} 个讲座, 其中 {available_lectures} 个可用. (第 {i + 1}/{args.times} 次检查)"
                )
                if available_lectures:
                    call_browser()
                    break
        else:
            lectures, available_lectures = fetch_lecture_list(session=session)
            render_table(lectures)
