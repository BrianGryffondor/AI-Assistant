import os
import requests
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class DeepSeekClient:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.base_url = "https://api.siliconflow.cn/v1"  # 根据实际API地址修改
        self.history: List[Dict] = []

    def chat(self, prompt: str) -> str:
        self._add_message("user", prompt)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",  # 根据实际模型名称修改
                "messages": self.history,
                "temperature": 0.7,
                "max_tokens": 5000
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"]
                self._add_message("assistant", ai_response)
                return ai_response
            else:
                return f"API错误: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"请求异常: {str(e)}"

    def _add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if len(self.history) > 6:
            self.history = self.history[-6:]