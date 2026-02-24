import eel
import os
import sys
from src.bridge import * # 导入所有暴露的函数

def start_app():
    # 确定 web 目录路径
    if getattr(sys, 'frozen', False):
        web_dir = os.path.join(sys._MEIPASS, 'web')
    else:
        web_dir = os.path.join(os.path.dirname(__file__), 'web')

    # 初始化 Eel
    eel.init(web_dir)

    # 启动应用
    # block=True 会阻塞进程直到窗口关闭
    try:
        eel.start('index.html', size=(1280, 800))
    except (SystemExit, KeyboardInterrupt):
        print("程序已关闭")

if __name__ == "__main__":
    start_app()
