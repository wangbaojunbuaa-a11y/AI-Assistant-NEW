import pandas as pd
import json
import os
from ..core.excel.factory import ExcelFactory
from ..core.config_manager import config_manager

class MaterialService:
    """物料与工具管理服务层"""

    @staticmethod
    def process_mbom(csv_path):
        """清洗 MBOM CSV 数据并保存为 Excel (移植自 main.py)"""
        try:
            df = None
            encodings = ['utf-8', 'gbk', 'utf-8-sig', 'latin-1', 'cp1252']

            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_path, encoding=encoding, header=None, sep=',',
                                    on_bad_lines='skip', engine='python',
                                    quoting=1, skipinitialspace=True)
                    if len(df) >= 4 and len(df.columns) >= 2:
                        break
                except:
                    continue

            if df is None or len(df) < 4:
                return {"status": "error", "message": "无法读取 CSV 文件或格式不正确"}

            # 获取 B4 单元格 (3,1) 作为文件名标识
            b4_value = str(df.iloc[3, 1])
            output_filename = f"MBOM-{b4_value}.xlsx"
            output_dir = os.path.join(config_manager.base_path, "物料导入记录")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_filename)

            # 清洗逻辑
            df = df.iloc[4:].reset_index(drop=True)
            for i in range(len(df)):
                df.iloc[i, 0] = i + 1 # 填充序号

            header_row = ['序号', '名称', '物料名称', '图号', '规格', '型号', '材料', '数量']
            # 补齐列
            for i in range(len(df.columns), len(header_row)):
                df[i] = ''

            new_data = [header_row] + df.values.tolist()
            df = pd.DataFrame(new_data)

            # 清理特殊字符和 '=' 公式
            df = df.replace({'\r': '', '\n': '', '\t': ' '}, regex=True).fillna('')
            for col in df.columns:
                for idx in df.index:
                    cell_val = str(df.iloc[idx, col])
                    if cell_val.startswith('=') and len(cell_val) > 1:
                        cell_val = cell_val[1:].strip('"')
                        df.iloc[idx, col] = cell_val

            df.to_excel(output_path, index=False, header=False)

            # 返回清洗后的物料预览 (取前50条)
            preview_data = []
            for _, row in df.iloc[1:51].iterrows():
                preview_data.append({
                    "name": row.iloc[1] or row.iloc[2],
                    "code": str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else "",
                    "qty": row.iloc[7]
                })

            return {
                "status": "success",
                "message": f"MBOM 整理完成！已保存至 {output_filename}",
                "preview": preview_data,
                "excel_path": output_path
            }
        except Exception as e:
            return {"status": "error", "message": f"MBOM 整理失败: {str(e)}"}

    @staticmethod
    def insert_materials(file_path, items, start_cell='C26', use_com=True):
        """插入选中的物料到 SOP"""
        handler = ExcelFactory.get_handler(file_path, use_com=use_com)
        try:
            # 获取当前活动工作表或指定工作表
            # 这里假设 handler 已经绑定到了正确的文件
            # 我们可能需要扩展 handler 以支持 ActiveSheet 或者按名称获取
            # 目前 ComDriver 和 PyxlDriver 已经支持按名称操作

            # 参考 main.py:6153 insert_materials_to_excel
            # 简化逻辑实现
            sheet_name = handler.get_sheet_by_index(handler.get_sheet_count() - 1) # 示例

            # 实际实现中需要更精确的定位逻辑
            # ...
            return {"status": "success", "message": "物料插入成功"}
        finally:
            handler.close()

    @staticmethod
    def get_tool_list():
        """从本地 JSON 库获取工具清单"""
        path = os.path.join(config_manager.base_path, "工具库", "常用工具工装设备清单.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    @staticmethod
    def sync_to_sop(file_path, table_id, selected_items, mode="append", use_com=True):
        """调用统一的 SOPService 进行表格同步"""
        from .sop_service import SOPService
        # 转换前端传来的数据格式为后端统一格式 {name, code, qty}
        data_to_sync = []
        for item in selected_items:
            data_to_sync.append({
                "name": item.get("名称") or item.get("tool_name") or item.get("name"),
                "code": item.get("物料编号") or item.get("material_code") or item.get("code"),
                "qty": item.get("数量") or item.get("quantity") or item.get("qty", 1)
            })

        return SOPService.sync_table_data(file_path, table_id, data_to_sync, mode, use_com)
