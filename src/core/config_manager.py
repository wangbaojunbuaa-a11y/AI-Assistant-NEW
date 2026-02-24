import os
import json
import sys

class ConfigManager:
    """统一配置与 JSON 数据库管理单例"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.base_path = self._get_base_path()
        self.config_dir = os.path.join(self.base_path, "config")

        # 确保配置目录存在
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        # 配置文件映射
        self.config_files = {
            "settings": "user_settings.json",
            "special_requirements": "special_requirements.json",
            "knowledge_base": "step_knowledge_base.json",
            "prompts": "prompt.json",
            "dify": "dify_config.json",
            "extract_template": "extract_template.json"
        }

        # 缓存加载的数据
        self._cache = {}
        self._initialized = True

    def _get_base_path(self):
        """获取程序根目录"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    def _get_file_path(self, key):
        """获取特定配置文件的绝对路径"""
        filename = self.config_files.get(key)
        if not filename:
            raise ValueError(f"Unknown config key: {key}")

        # 优先从 config/ 目录读取，如果不存在则尝试从根目录读取（兼容旧版）
        path = os.path.join(self.config_dir, filename)
        if not os.path.exists(path):
            old_path = os.path.join(self.base_path, filename)
            if os.path.exists(old_path):
                return old_path
        return path

    def get(self, key, default=None):
        """获取配置内容（带缓存）"""
        if key in self._cache:
            return self._cache[key]

        path = self._get_file_path(key)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._cache[key] = data
                    return data
            except Exception as e:
                print(f"[错误] 加载配置 {key} 失败: {e}")

        return default if default is not None else {}

    def save(self, key, data):
        """保存配置内容并更新缓存"""
        self._cache[key] = data
        path = self._get_file_path(key)

        # 如果是在根目录的旧文件，且 config/ 目录已存在，则保存到 config/
        if not path.startswith(self.config_dir):
            path = os.path.join(self.config_dir, self.config_files[key])

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"[错误] 保存配置 {key} 失败: {e}")
            return False

    def get_setting(self, path, default=None):
        """获取 settings.json 中的嵌套项，例如 'deepseek_config.api_key'"""
        settings = self.get("settings")
        keys = path.split('.')
        value = settings
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

# 全局单例
config_manager = ConfigManager()
