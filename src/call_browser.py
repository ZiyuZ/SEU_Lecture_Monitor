import webbrowser

from config import Config as C


def call_browser():
    webbrowser.open(C.URLs.lecture_page, new=0, autoraise=True)


if __name__ == "__main__":
    call_browser()
