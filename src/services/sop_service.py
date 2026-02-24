import time
import os
from ..core.excel.factory import ExcelFactory
from ..core.config_manager import config_manager

class SOPService:
    """SOP 业务逻辑服务层 (抽象统一版)"""

    @staticmethod
    def _get_template():
        return config_manager.get("templates")

    @staticmethod
    def update_metadata(file_path, field_type, new_value, use_com=True):
        handler = ExcelFactory.get_handler(file_path, use_com=use_com)
        template = SOPService._get_template().get("metadata", {}).get(field_type)
        try:
            count = handler.get_sheet_count()
            for i in range(count):
                sheet_name = handler.get_sheet_by_index(i)
                cfg = template["first_page"] if i == 0 else template["other_pages"]
                label_val = str(handler.get_value(sheet_name, cfg["label_cell"])).strip()
                if label_val == cfg["label_text"]:
                    handler.set_value(sheet_name, cfg["value_cell"], new_value)
            handler.save()
            return {"status": "success", "message": f"{field_type} 更新成功"}
        finally:
            handler.close()

    @staticmethod
    def write_content_block(file_path, block_type, text, mode="append", use_com=True):
        handler = ExcelFactory.get_handler(file_path, use_com=use_com)
        cfg = SOPService._get_template().get("blocks", {}).get(block_type)
        try:
            sheet_name = cfg.get("sheet") or handler.get_sheet_by_index(handler.get_sheet_count() - 1)
            cell = cfg["cell"]
            existing = str(handler.get_value(sheet_name, cell) or "").strip()
            if mode == "append" and existing:
                if text in existing: return {"status": "info", "message": "内容已存在"}
                new_text = existing + "\n\n" + text
            else:
                new_text = text
            handler.set_value(sheet_name, cell, new_text)
            handler.save()
            return {"status": "success", "message": "内容写入成功"}
        finally:
            handler.close()

    @staticmethod
    def update_page_numbers(file_path, use_com=True):
        handler = ExcelFactory.get_handler(file_path, use_com=use_com)
        template = SOPService._get_template().get("metadata", {}).get("page_number")
        try:
            total_pages = handler.get_sheet_count()
            cfg = template["all_pages"]
            for i in range(total_pages):
                sheet_name = handler.get_sheet_by_index(i)
                label_val = str(handler.get_value(sheet_name, cfg["label_cell"])).strip()
                if label_val == cfg["label_text"]:
                    handler.set_value(sheet_name, cfg["value_cell"], f"第{i+1}页 共{total_pages}页")
            handler.save()
            return {"status": "success", "message": "页码更新完成"}
        finally:
            handler.close()

    @staticmethod
    def sync_table_data(file_path, table_id, data_list, mode="append", use_com=True):
        handler = ExcelFactory.get_handler(file_path, use_com=use_com)
        cfg = SOPService._get_template().get("tables", {}).get(table_id)
        try:
            sheet_name = cfg.get("sheet_name") or handler.get_sheet_by_index(handler.get_sheet_count() - 1)
            start_row, row_step, cols = cfg["start_row"], cfg["row_step"], cfg["columns"]
            if mode == "overwrite":
                for r in range(start_row, start_row + 20, row_step):
                    for col in cols.values(): handler.set_cell_by_index(sheet_name, r, ord(col) - 64, "")
            current_row = start_row
            for item in data_list:
                if mode == "append":
                    while True:
                        if not handler.get_cell_by_index(sheet_name, current_row, ord(cols["name"]) - 64): break
                        current_row += row_step
                handler.set_cell_by_index(sheet_name, current_row, ord(cols["name"]) - 64, item.get("name", ""))
                handler.set_cell_by_index(sheet_name, current_row, ord(cols["code"]) - 64, item.get("code", ""))
                handler.set_cell_by_index(sheet_name, current_row, ord(cols["qty"]) - 64, item.get("qty", ""))
                current_row += row_step
            handler.save()
            return {"status": "success", "message": "同步成功"}
        finally:
            handler.close()

    @staticmethod
    def analyze_image(file_path, range_str="R12:AQ55"):
        from ..core.ai_client import DifyClient
        handler = ExcelFactory.get_handler(file_path, use_com=True)
        image_dir = os.path.join(config_manager.base_path, "图片库")
        os.makedirs(image_dir, exist_ok=True)
        try:
            sheet_name = handler.get_sheet_by_index(handler.get_sheet_count() - 1)
            save_path = os.path.join(image_dir, f"audit_{int(time.time())}.png")
            if handler.capture_range_image(sheet_name, range_str, save_path):
                dify = DifyClient()
                file_id = dify.upload_file(save_path)
                result = dify.vision_chat("请根据图片审核工步操作是否合规", file_id)
                return {"status": "success", "result": result, "image_path": save_path}
            return {"status": "error", "message": "截图失败"}
        finally:
            handler.close()
