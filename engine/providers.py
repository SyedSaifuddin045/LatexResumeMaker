import requests
import json
import google.generativeai as genai
from abc import ABC, abstractmethod

class AIProvider(ABC):
    def __init__(self, api_key, model, api_base=None):
        self.api_key = api_key
        self.model = model
        self.api_base = api_base

    @abstractmethod
    def generate_text(self, system, prompt):
        pass

    @abstractmethod
    def generate_json(self, system, prompt):
        pass

class OpenAIProvider(AIProvider):
    def __init__(self, api_key, model, api_base="https://api.openai.com/v1"):
        super().__init__(api_key, model, api_base)

    def _call(self, system, prompt, json_mode=False):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        }
        if json_mode:
            data["response_format"] = {"type": "json_object"}

        response = requests.post(f"{self.api_base}/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return json.loads(content) if json_mode else content

    def generate_text(self, system, prompt):
        return self._call(system, prompt, json_mode=False)

    def generate_json(self, system, prompt):
        return self._call(system, prompt, json_mode=True)

class GoogleProvider(AIProvider):
    def __init__(self, api_key, model):
        super().__init__(api_key, model)
        genai.configure(api_key=api_key)

    def _call(self, system, prompt, json_mode=False):
        model = genai.GenerativeModel(self.model)
        full_prompt = f"{system}\n\n{prompt}"
        config = {"response_mime_type": "application/json"} if json_mode else None
        
        response = model.generate_content(full_prompt, generation_config=config)
        return json.loads(response.text) if json_mode else response.text

    def generate_text(self, system, prompt):
        return self._call(system, prompt, json_mode=False)

    def generate_json(self, system, prompt):
        return self._call(system, prompt, json_mode=True)

class OllamaProvider(AIProvider):
    def __init__(self, api_key, model, api_base="http://localhost:11434"):
        super().__init__(api_key, model, api_base)

    def _call(self, system, prompt, json_mode=False):
        url = f"{self.api_base}/api/generate"
        data = {
            "model": self.model,
            "system": system,
            "prompt": prompt,
            "stream": False
        }
        if json_mode:
            data["format"] = "json"
            
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        content = response.json()['response']
        return json.loads(content) if json_mode else content

    def generate_text(self, system, prompt):
        return self._call(system, prompt, json_mode=False)

    def generate_json(self, system, prompt):
        return self._call(system, prompt, json_mode=True)
