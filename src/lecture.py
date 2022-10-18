import sys
import time
from typing import Dict, List, Tuple

import requests
from rich.console import Console
from rich.table import Table

from config import Config as C

LC = C.Lecture


class Lecture:
    id: str
    name: str
    introduction: str
    lecture_type: str
    place: str
    presenter: str
    person_number: int
    seat_number: int
    reserve_time: str
    lecture_time: str
    status: LC.Status

    def __init__(self, raw_lecture):
        columns = LC.Fields
        self.id = raw_lecture[columns.ID]
        self.name = raw_lecture[columns.Name].replace("【线上】", "🌐").replace("【线下】", "🏫")
        self.introduction = raw_lecture[columns.Introduction]
        self.lecture_type = raw_lecture[columns.Type]
        self.place = (
            raw_lecture[columns.Place].replace("腾讯会议", "🐧腾讯会议").replace("校区", " | ")
        )
        self.presenter = raw_lecture[columns.Presenter]

        self.person_number = int(raw_lecture[columns.PersonNum])
        self.seat_number = int(raw_lecture[columns.SeatNum])

        # 去掉年和秒
        self.reserve_time = raw_lecture[columns.ReserveTime][5:-3]
        self.lecture_time = raw_lecture[columns.LectureTime][5:-3]

        self.status = self.parse_status(
            raw_lecture[columns.LectureStatus], raw_lecture[columns.ReleaseStatus]
        )
        self.prune()

    def parse_status(self, lecture_status, release_status) -> LC.Status:
        if release_status != "1":
            return LC.Status.Disabled
        if lecture_status == 0:
            return LC.Status.Locked
        if self.person_number < self.seat_number:
            return LC.Status.Vacant
        if self.person_number == self.seat_number:
            return LC.Status.Full
        raise ValueError(f"Unknown status({lecture_status=}, {release_status=})")

    def prune(self):
        self.lecture_type = LC.SubRegex.type.sub("", self.lecture_type)
        self.name = LC.SubRegex.name.sub("", self.name)
        self.place = LC.SubRegex.place.sub("", self.place)

    def table_format(self) -> List[str]:
        if self.is_vacant() or self.is_full():
            number_display = f"{self.person_number}/{self.seat_number}"
        else:
            number_display = str(self.seat_number)
        return [
            self.status.value,
            number_display,
            self.name,
            self.place,
            self.lecture_type,
            self.reserve_time,
            self.lecture_time,
        ]

    def is_locked(self) -> bool:
        return self.status is LC.Status.Locked

    def is_full(self) -> bool:
        return self.status is LC.Status.Full

    def is_vacant(self) -> bool:
        return self.status is LC.Status.Vacant

    def is_disabled(self) -> bool:
        return self.status is LC.Status.Disabled

    def __str__(self) -> str:
        return " ".join(self.table_format())


class LectureList:
    session: requests.Session
    lectures: List[Lecture]
    # opened: vacant or full; enabled: vacant or full or locked
    opened_count: int
    vacant_count: int

    def __init__(self, session: requests.Session):
        self.session = session
        self.lectures = []
        self.opened_count = 0
        self.vacant_count = 0

    def fetch(self):
        res = self.session.get(C.URLs.lecture_list)
        raw_lectures: List[Dict] = res.json()["datas"]
        self.lectures.clear()
        for rl in raw_lectures[::-1]:
            l = Lecture(rl)
            if l.is_vacant():
                self.vacant_count += 1
                self.opened_count += 1
                self.lectures.insert(0, l)
                continue
            if l.is_full():
                self.opened_count += 1
            self.lectures.append(l)

    def render_table(self, with_disabled=False):
        # 没有讲座时直接返回
        count = len(self.lectures)
        if count == 0:
            C.logger.info("❌ No lecture found.")
            return
        C.logger.info("💖 Found %d lecture%s enabled.", count, ["s.", "."][count == 1])
        # 渲染讲座
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        # 表头
        for column in LC.render_columns:
            table.add_column(column, justify="center")
        # 讲座
        for lecture in self.lectures:
            C.logger.debug(lecture)
            if lecture.is_disabled() and not with_disabled:
                C.logger.debug("Current lecture is disabled, skip.")
                continue
            status = lecture.status
            table.add_row(status.value, *lecture.table_format(), style=status.color())

        console.print(table)
        console.print(
            "[dim i][bold]Link of Lectures:[/bold][/dim i]\n",
            f"   [dim i]{C.URLs.lecture_page}[/dim i]",
        )

    def check_vacant(self, times: int, interval: int) -> bool:
        C.logger.info("开始定时检查讲座: 每 %s 秒, 共 %s 次. 按下 `Ctrl + C` 中断.\n", interval, times)
        for i in range(times):
            if i:  # sleep when i > 0
                time.sleep(interval)
            self.fetch()
            if not self.opened_count:
                C.logger.info("🔒 All lectures are locked.")
                self.render_table()
                sys.exit(0)
            # 检查是否有开放的讲座
            C.logger.info(
                "发现 %s 个讲座, 其中 %s 个可用. (第 %s/%s 次检查)",
                len(self.lectures),
                self.vacant_count,
                i + 1,
                times,
            )
            if self.vacant_count:
                print("\a")  # notification sound
                return True
        return False
