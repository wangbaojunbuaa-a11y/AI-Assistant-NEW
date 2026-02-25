import eel
import os
import sys

# 尝试相对导入，如果失败则使用绝对导入
try:
    from .services.sop_service import SOPService
    from .services.material_service import MaterialService
    from .services.catalog_service import CatalogService
    from .core.ai_client import DeepSeekClient, DifyClient
    from .core.config_manager import config_manager
except ImportError:
    # PyInstaller 打包后的环境
    from src.services.sop_service import SOPService
    from src.services.material_service import MaterialService
    from src.services.catalog_service import CatalogService
    from src.core.ai_client import DeepSeekClient, DifyClient
    from src.core.config_manager import config_manager

# 初始化 AI 客户端
deepseek = DeepSeekClient()
dify = DifyClient()

@eel.expose
def get_config(key):
    return config_manager.get(key)

@eel.expose
def save_config(key, data):
    return config_manager.save(key, data)

@eel.expose
def get_knowledge_base():
    """获取工步知识库数据"""
    return config_manager.get("knowledge_base").get("工步知识库", [])

@eel.expose
def generate_sop_catalog(file_path):
    return CatalogService.generate(file_path)

@eel.expose
def get_pdf_rules():
    """获取通用操作守则目录下的 PDF 文件列表"""
    path = os.path.join(config_manager.base_path, "通用操作守则")
    if not os.path.exists(path):
        return []

    pdfs = []
    for f in os.listdir(path):
        if f.lower().endswith('.pdf'):
            pdfs.append(f)
    return sorted(pdfs)

@eel.expose
def get_special_requirements():
    return config_manager.get("special_requirements")

@eel.expose
def update_sop_page_numbers(file_path):
    return SOPService.update_page_numbers(file_path, use_com=True)

@eel.expose
def update_sop_metadata(file_path, field_type, new_value):
    """
    field_type: 'file_number' or 'version'
    """
    return SOPService.update_metadata(file_path, field_type, new_value, use_com=True)

@eel.expose
def write_sop_block(file_path, block_type, text, mode="append"):
    """
    block_type: 'process_requirement', 'operation_content', 'control_method', 'special_requirement'
    """
    return SOPService.write_content_block(file_path, block_type, text, mode, use_com=True)

@eel.expose
def audit_sop_image(file_path):
    return SOPService.analyze_image(file_path)

@eel.expose
def ai_generate_content(prompt, workflow_type=None):
    """调用 AI 生成内容"""
    try:
        # 使用流式回调更新前端（可选）
        def sync_callback(chunk, full):
            eel.on_ai_chunk(chunk, full)

        result = deepseek.simple_chat(prompt, workflow_type=workflow_type, stream=True, stream_callback=sync_callback)
        return {"status": "success", "content": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@eel.expose
def pick_and_process_mbom():
    """打开文件对话框并处理 MBOM"""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    file_path = filedialog.askopenfilename(title="选择原始 MBOM CSV 文件", filetypes=[("CSV Files", "*.csv")])
    root.destroy()

    if not file_path:
        return {"status": "cancel"}

    return MaterialService.process_mbom(file_path)

@eel.expose
def get_tools():
    return MaterialService.get_tool_list()

@eel.expose
def sync_sop_table(file_path, table_id, items, mode="append"):
    """
    table_id: 'material' or 'tool'
    """
    return MaterialService.sync_to_sop(file_path, table_id, items, mode, use_com=True)

@eel.expose
def list_open_excel_files():
    """列出当前打开的 Excel 文件（需要扩展 ComDriver）"""
    # 这里可以调用 win32com 获取所有打开的工作簿
    import win32com.client
    try:
        excel = win32com.client.GetActiveObject("Excel.Application")
        return [wb.FullName for wb in excel.Workbooks]
    except:
        return []
