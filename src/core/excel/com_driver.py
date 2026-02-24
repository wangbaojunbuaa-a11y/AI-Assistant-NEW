import win32com.client
import pythoncom
from .base import ExcelHandler

class ComDriver(ExcelHandler):
    """使用 win32com 处理已打开或加密的 Excel 文件"""

    def __init__(self, path=None, workbook=None):
        pythoncom.CoInitialize()
        self.excel_app = None
        self.wb = workbook
        self.path = path

        if not self.wb and path:
            self._open_by_path(path)

    def _open_by_path(self, path):
        try:
            self.excel_app = win32com.client.GetActiveObject("Excel.Application")
            for wb in self.excel_app.Workbooks:
                if wb.FullName.lower() == path.lower():
                    self.wb = wb
                    break
            if not self.wb:
                self.wb = self.excel_app.Workbooks.Open(path)
        except Exception:
            self.excel_app = win32com.client.Dispatch("Excel.Application")
            self.wb = self.excel_app.Workbooks.Open(path)

        self.excel_app.Visible = True

    def get_value(self, sheet_name, cell_address):
        sheet = self.wb.Worksheets(sheet_name)
        return sheet.Range(cell_address).Value

    def set_value(self, sheet_name, cell_address, value):
        sheet = self.wb.Worksheets(sheet_name)
        sheet.Range(cell_address).Value = value

    def get_cell_by_index(self, sheet_name, row, col):
        sheet = self.wb.Worksheets(sheet_name)
        return sheet.Cells(row, col).Value

    def set_cell_by_index(self, sheet_name, row, col, value):
        sheet = self.wb.Worksheets(sheet_name)
        sheet.Cells(row, col).Value = value

    def get_sheet_count(self):
        return self.wb.Worksheets.Count

    def get_sheet_by_index(self, index):
        # COM is 1-based, our index is 0-based
        return self.wb.Worksheets(index + 1).Name

    def capture_range_image(self, sheet_name, range_str, save_path):
        import win32clipboard
        from PIL import ImageGrab
        import time

        sheet = self.wb.Worksheets(sheet_name)
        sheet.Activate()
        rng = sheet.Range(range_str)
        rng.CopyPicture(Appearance=1, Format=2) # xlScreen=1, xlBitmap=2

        time.sleep(0.5) # 等待剪贴板就绪
        img = ImageGrab.grabclipboard()
        if img:
            img.save(save_path, "PNG")
            return True
        return False

    def copy_sheet_from_external(self, source_path, source_sheet_name, target_sheet_name, after_sheet_index=None):
        temp_wb = self.excel_app.Workbooks.Open(source_path)
        try:
            source_sheet = temp_wb.Worksheets(source_sheet_name)

            if after_sheet_index is not None:
                after_sheet = self.wb.Worksheets(after_sheet_index)
                source_sheet.Copy(After=after_sheet)
            else:
                source_sheet.Copy(After=self.wb.Worksheets(self.wb.Worksheets.Count))

            new_sheet = self.wb.ActiveSheet
            new_sheet.Name = target_sheet_name
            return True
        finally:
            temp_wb.Close(False)

    def merge_cells(self, sheet_name, range_str):
        sheet = self.wb.Worksheets(sheet_name)
        sheet.Range(range_str).Merge()

    def get_sheet_names(self):
        return [sheet.Name for sheet in self.wb.Worksheets]

    def save(self, path=None):
        if path:
            self.wb.SaveAs(path)
        else:
            self.wb.Save()

    def close(self):
        # 注意：ComDriver 通常不强制关闭 Excel 程序，只释放引用
        self.wb = None
        self.excel_app = None
        pythoncom.CoUninitialize()
