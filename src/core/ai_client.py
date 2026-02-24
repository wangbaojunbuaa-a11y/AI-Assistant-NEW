import json
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config_manager import config_manager

class DeepSeekClient:
    """DeepSeek API 客户端类"""

    def __init__(self, api_base=None, api_key=None, model=None, temperature=None, max_tokens=None, timeout=None):
        deepseek_config = config_manager.get("settings").get("deepseek_config", {})

        self.api_base = api_base or deepseek_config.get("api_base", "http://192.168.0.3:1025/v1")
        self.api_key = api_key or deepseek_config.get("api_key", "null")
        self.model = model or deepseek_config.get("model", "DeepSeek-V3.1")
        self.temperature = temperature if temperature is not None else deepseek_config.get("temperature", 0.7)
        self.max_tokens = max_tokens if max_tokens is not None else deepseek_config.get("max_tokens", 2048)
        self.timeout = timeout if timeout is not None else deepseek_config.get("timeout", 300)

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def chat_completion(self, messages, stream=False):
        url = f"{self.api_base}/chat/completions"
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": stream
        }

        try:
            response = self.session.post(url, json=data, timeout=self.timeout, stream=stream)
            response.raise_for_status()

            if stream:
                return self._parse_stream_response(response)
            return response.json()
        except Exception as e:
            print(f"[错误] DeepSeek API 调用失败: {e}")
            raise

    def _parse_stream_response(self, response):
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str.strip() == '[DONE]':
                        break
                    try:
                        yield json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

    def simple_chat(self, prompt, workflow_type=None, stream=False, stream_callback=None):
        """单轮对话，支持从 prompt.json 自动获取前缀"""
        prompt_prefix = ""
        if workflow_type:
            prompts = config_manager.get("prompts")
            prompt_prefix = prompts.get(workflow_type, "")

        final_content = f"{prompt_prefix}\n\n{prompt}" if prompt_prefix else prompt
        messages = [{"role": "user", "content": final_content}]

        if not stream:
            result = self.chat_completion(messages, stream=False)
            return result['choices'][0]['message']['content']

        # 流式处理
        full_content = ""
        for chunk in self.chat_completion(messages, stream=True):
            delta = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
            if delta:
                full_content += delta
                if stream_callback:
                    stream_callback(delta, full_content)
        return full_content

class DifyClient:
    """Dify API 客户端类（用于视觉/图像分析）"""
    def __init__(self):
        self.config = config_manager.get("dify")
        self.api_key = self.config.get("api_key")
        self.base_url = self.config.get("base_url", "https://api.dify.ai/v1")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def upload_file(self, file_path):
        url = f"{self.base_url}/files/upload"
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'image/png')}
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(url, headers=headers, files=files, data={'user': 'ai-assistant'})
            response.raise_for_status()
            return response.json().get('id')

    def vision_chat(self, query, file_id):
        url = f"{self.base_url}/chat-messages"
        data = {
            "inputs": {
                "pic": {
                    "transfer_method": "local_file",
                    "upload_file_id": file_id,
                    "type": "image"
                }
            },
            "query": query,
            "response_mode": "blocking",
            "user": "ai-assistant"
        }
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json().get('answer')
