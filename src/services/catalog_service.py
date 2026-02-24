import os
from ..core.excel.factory import ExcelFactory
from ..core.config_manager import config_manager

class CatalogService:
    """SOP 目录生成服务层 (完整版)"""

    @staticmethod
    def _get_template_cfg():
        return config_manager.get("templates").get("catalog", {})

    @staticmethod
    def generate(file_path, template_path=None):
        """
        全流程生成 SOP 目录：提取数据 -> 插入模板 -> 多栏填充
        """
        if not template_path:
            template_path = os.path.join(config_manager.base_path, "catalog_template.xlsx")

        handler = ExcelFactory.get_handler(file_path, use_com=True)
        cfg = CatalogService._get_template_cfg()

        try:
            # 1. 提取数据
            catalog_data = []
            total_sheets = handler.get_sheet_count()
            extract_cfg = cfg.get("extraction", {})
            trigger = extract_cfg.get("trigger_label", {})

            for i in range(total_sheets):
                sheet_name = handler.get_sheet_by_index(i)
                # 检查是否是工序页
                label = str(handler.get_value(sheet_name, trigger["cell"])).strip()
                if label == trigger["text"]:
                    fields = extract_cfg.get("fields", {})
                    catalog_data.append({
                        "p_num": str(handler.get_value(sheet_name, fields["process_num"]) or ""),
                        "p_name": str(handler.get_value(sheet_name, fields["process_name"]) or ""),
                        "s_num": str(handler.get_value(sheet_name, fields["step_num"]) or ""),
                        "s_name": str(handler.get_value(sheet_name, fields["step_name"]) or ""),
                        "page": i + 1
                    })

            if not catalog_data:
                return {"status": "error", "message": "未在文件中找到带有'页数'标记的工序页"}

            # 2. 准备目录页 (创建新 Sheet)
            catalog_sheet_name = "目录"
            # 如果已存在，则尝试重命名为 目录_1, 目录_2...
            existing_names = handler.get_sheet_names()
            if catalog_sheet_name in existing_names:
                # 实际原逻辑是提示删除，这里我们简单处理，先尝试复制
                pass

            # 从模板复制
            handler.copy_sheet_from_external(template_path, "目录", catalog_sheet_name, after_sheet_index=2)

            # 3. 填充数据 (双栏逻辑)
            fill_cfg = cfg.get("filling", {})
            curr_row = fill_cfg["start_row"]
            max_row = fill_cfg["max_row"]
            is_left = True

            for item in catalog_data:
                # 检查是否需要切栏或切页 (简化实现：单页双栏)
                if curr_row > max_row:
                    if is_left:
                        is_left = False
                        curr_row = fill_cfg["start_row"]
                    else:
                        # 实际需要增加新目录页，此处暂记日志
                        break

                cols = fill_cfg["left_cols"] if is_left else fill_cfg["right_cols"]

                handler.set_cell_by_index(catalog_sheet_name, curr_row, cols["process_num"], item["p_num"])
                handler.set_cell_by_index(catalog_sheet_name, curr_row, cols["process_name"], item["p_name"])
                handler.set_cell_by_index(catalog_sheet_name, curr_row, cols["step_num"], item["s_num"])
                handler.set_cell_by_index(catalog_sheet_name, curr_row, cols["step_name"], item["s_name"])
                handler.set_cell_by_index(catalog_sheet_name, curr_row, cols["page"], item["page"])

                curr_row += 1

            handler.save()
            return {"status": "success", "message": f"目录已生成，共提取 {len(catalog_data)} 条工序数据。"}

        except Exception as e:
            return {"status": "error", "message": f"目录生成失败: {str(e)}"}
        finally:
            handler.close()
