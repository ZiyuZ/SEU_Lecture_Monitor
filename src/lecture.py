import requests
from rich.console import Console
from rich.table import Table

from config import Config as C
from login import login_ehall


def fetch_lecture_list(session: requests.Session) -> list:
    res = session.get(C.URLs.lecture_list)
    lectures = res.json()["datas"]
    # 过滤多余内容
    for lecture in lectures:
        lecture["JZXL_DISPLAY"] = lecture["JZXL_DISPLAY"].replace("人文与科学素养系列讲座_", "")
        lecture["SFKSYY"] = "❌" if lecture["SFKSYY"] == 0 else "✔"
        lecture["YYRS_HDZRS"] = f'{lecture["YYRS"]}/{lecture["HDZRS"]}'
    return lectures


def render_table(lectures: list):
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


if __name__ == "__main__":
    session, student_name = login_ehall(C.username, C.password)
    if student_name:
        C.logger.info(f"✨ {'***' if C.privacy_mode else student_name}, Welcome! ✨")
        lectures = fetch_lecture_list(session=session)
        render_table(lectures)
