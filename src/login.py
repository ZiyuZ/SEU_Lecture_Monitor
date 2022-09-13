from pathlib import Path
from typing import Tuple

import js2py
import requests
from pyquery import PyQuery as pq

from config import Config as C

# from rich.console import Console
# console = Console()


def encrypt(data: str, salt: str) -> str:
    # 执行整段JS代码
    context = js2py.EvalJs()
    context.execute(Path(C.encrypt_js).read_text())
    result = context.encryptAES(data, salt)
    # C.logger.debug("encrypt result:" + result)
    return result


# 登录信息门户，返回登录后的session
def login_ehall(username: str, password: str) -> Tuple[requests.Session, str]:

    C.logger.info(f"✨ Login id: {'***' if C.privacy_mode else username} ✨")
    session = requests.Session()

    # 获取登陆页面 hidden salt
    res = session.get(C.URLs.login_page)
    doc = pq(res.text)
    # 填充 form
    form = {"username": username}
    for el in doc('div[tabid="01"] input[type="hidden"][name]'):
        form[el.name] = el.value
    # 处理密码
    salt = doc('div[tabid="01"] input[type="hidden"][id]')[0]
    # salt.get('id') == 'pwdDefaultEncryptSalt'
    form[salt.get("id")] = salt.value
    form["password"] = encrypt(password, salt.value)
    C.logger.debug(form)
    # 登录认证
    res = session.post(C.URLs.login_page, data=form)
    # 判断是否成功
    doc = pq(res.text)
    student_name = doc(".auth_username > span > span")
    if student_name:
        student_name = student_name[0].text.strip()
        return session, student_name
    else:
        C.logger.error("认证失败！" + doc("#msg").text())
        return session, ""
