from abc import ABC, abstractmethod

class ExcelHandler(ABC):
    """Excel 处理抽象基类"""

    @abstractmethod
    def get_value(self, sheet_name, cell_address):
        """获取单元格值"""
        pass

    @abstractmethod
    def set_value(self, sheet_name, cell_address, value):
        """设置单元格值"""
        pass

    @abstractmethod
    def get_cell_by_index(self, sheet_name, row, col):
        """通过行列索引获取值 (1-based)"""
        pass

    @abstractmethod
    def set_cell_by_index(self, sheet_name, row, col, value):
        """通过行列索引设置值 (1-based)"""
        pass

    @abstractmethod
    def get_sheet_count(self):
        """获取工作表数量"""
        pass

    @abstractmethod
    def get_sheet_by_index(self, index):
        """通过索引获取工作表名称 (0-based)"""
        pass

    @abstractmethod
    def capture_range_image(self, sheet_name, range_str, save_path):
        """截取指定区域并保存为图片"""
        pass

    @abstractmethod
    def copy_sheet_from_external(self, source_path, source_sheet_name, target_sheet_name, after_sheet_index=None):
        """从外部工作簿复制工作表"""
        pass

    @abstractmethod
    def merge_cells(self, sheet_name, range_str):
        """合并单元格"""
        pass

    @abstractmethod
    def get_sheet_names(self):
        """获取所有工作表名称"""
        pass

    @abstractmethod
    def save(self, path=None):
        """保存文件"""
        pass

    @abstractmethod
    def close(self):
        """关闭文件/释放资源"""
        pass
