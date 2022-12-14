# SEU Lecture Monitor

自动登录并检查讲座状态，检查过程不依赖浏览器/webdriver。

开发环境：python 3.8 (理论上 >= 3.7 即可), 项目采用 [PDM - Python Development Master](https://pdm.fming.dev/) 管理。

## 使用指南

1. 克隆项目或下载并解压到本地并进入项目目录
2. 重命名 `.env.example` 为 `.env`，使用文本编辑器打开, 分别修改字段 `SEU_USERNAME` 与 `SEU_PASSWORD` 内容为你的账号及密码
   - 请注意: **密码以明文形式存放, 请注意保护文件安全**, 也许会考虑改为以参数形式传入密码.
3. 如果你:
   - 使用 pip/conda/mamba：
     1. 使用你的包管理器安装依赖：`pip install requests js2py pyquery environs rich`
        - 也可以新建一个虚拟环境
     2. 在目录下执行 `python ./src/entry.py`
     3. 如果有想要选取的讲座，执行 `python ./src/entry.py -b` 将打开浏览器并跳转到讲座网页，可能需要登录
     4. 如果想定时检查是否有可用的讲座 (可预约且有名额), 执行 `python ./src/entry.py -r -i <检查间隔> -t <检查次数>`, 此时如果有可用讲座将自动打开浏览器
   - 使用 `pdm`：
     1. 安装依赖：`pdm install`
     2. 在目录下执行 `pdm run lecture`
     3. 如果有想要选取的讲座，执行 `pdm run web` 将打开浏览器并跳转到讲座网页，可能需要登录
     4. 如果想定时检查是否有可用的讲座 (可预约且有名额), 执行 `pdm run lecture -r -i <检查间隔> -t <检查次数>`, 此时如果有可用讲座将自动打开浏览器
4. 或者复制执行结果底部提供的链接并在浏览器中访问

_注意: SEU Lecture Monitor 使用了一些 emoji 符号用于展示信息, 你可能需要使用支持 emoji 的终端模拟器与字体._

_不想每次打开浏览器都登录: 使用支持多标签页的浏览器, 登陆后不要关闭浏览器, 这样会保留登录状态, 下次打开时会直接跳转到讲座页面._

你可以在你的 shell profile 中设置 alias 以便快捷访问, 例如 Powershell:

```powershell
function slm {
  $cur = Get-Location
  cd <SEU_Lecture_Monitor_Path>
  pdm run lecture $args  # 或者 `python ./src/entry.py $args`, 如果你不使用 pdm
  cd $cur
}
```

## 截图

- 登陆失败时
  - 请检查 `.env` 中的用户名和密码是否正确


![image-20220913200125428](assets/failure.png)

- 成功获取到讲座, 其中
  - "📌" 列为讲座状态: "🔒" 表示未到预约时间, "✅" 表示可预约, "🛑" 表示人满.
  - "🔖 名称" 列为讲座名称: "🏫" 表示线下讲座, "🌐" 表示线上讲座, 但不是所有的讲座都标注了线上或线下, 请结合 "📍 地点" 确认.


![image-20221018015653371](assets/success.png)

- 没有获取到讲座

![image-20220913200257811](assets/no_lecture.png)

- 定时检查讲座
  - 当检测到有可用讲座时, 将自动打开讲座预约页面, 请在网页打开后手动预约讲座
  - 建议检查间隔在 15 秒以上


![image-20221011214711215](assets/repeat.png)

## 声明

**⚠️ 项目是出于学习目的编写的，仅能获取讲座状态，不具备也没有计划实现预约讲座功能 ⚠️**

## 特别感谢

- 模拟登录代码修改自 [luzy99/SEUAutoLogin: 东南大学信息门户自动登录，SEU 每日自动健康打卡，附赠绩点计算功能。Github Action 一键部署，自动打卡](https://github.com/luzy99/SEUAutoLogin)
