import os
from .com_driver import ComDriver
from .pyxl_driver import PyxlDriver

class ExcelFactory:
    """Excel 处理工厂"""

    @staticmethod
    def get_handler(path, use_com=False):
        """
        获取合适的 Excel 处理器
        :param path: 文件路径
        :param use_com: 是否强制使用 COM 接口（处理加密或已打开文件）
        """
        if use_com:
            return ComDriver(path=path)

        # 默认逻辑：如果文件正在运行中，建议使用 COM
        # 这里简单处理，可根据需求增加检测逻辑
        try:
            return PyxlDriver(path)
        except Exception:
            # 如果 openpyxl 失败（如文件被锁定），尝试 COM
            return ComDriver(path=path)
