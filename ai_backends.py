# ai_backends.py
import openai
from transformers import pipeline
import requests
from config import config

class AIBackend:
    def get_organization_suggestions(self, file_list):
        raise NotImplementedError

class OpenAIBackend(AIBackend):
    def __init__(self):
        openai.api_key = config.get("openai_api_key")

    def get_organization_suggestions(self, file_list):
        prompt = f"Analyze the following list of files and suggest an efficient organization structure:\n\n{file_list}\n\nProposed organization:"
        response = openai.Completion.create(
            engine=config.get("openai_model"),
            prompt=prompt,
            max_tokens=config.get("max_tokens"),
            n=1,
            stop=None,
            temperature=config.get("temperature")
        )
        return response.choices[0].text.strip()

class HuggingFaceBackend(AIBackend):
    def __init__(self):
        self.api_url = f"https://api-inference.huggingface.co/models/{config.get('huggingface_model')}"
        self.headers = {"Authorization": f"Bearer {config.get('huggingface_api_key')}"}

    def get_organization_suggestions(self, file_list):
        prompt = f"Analyze the following list of files and suggest an efficient organization structure:\n\n{file_list}\n\nProposed organization:"
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": config.get("max_tokens"),
                "temperature": config.get("temperature")
            }
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()[0]["generated_text"].strip()

class LocalModelBackend(AIBackend):
    def __init__(self):
        model_path = config.get("local_model_path")
        self.pipeline = pipeline("text-generation", model=model_path)

    def get_organization_suggestions(self, file_list):
        prompt = f"Analyze the following list of files and suggest an efficient organization structure:\n\n{file_list}\n\nProposed organization:"
        result = self.pipeline(prompt, max_new_tokens=config.get("max_tokens"), temperature=config.get("temperature"))
        return result[0]["generated_text"].strip()

class PerplexityBackend(AIBackend):
    def __init__(self):
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {config.get('perplexity_api_key')}",
            "Content-Type": "application/json"
        }

    def get_organization_suggestions(self, file_list):
        prompt = f"Analyze the following list of files and suggest an efficient organization structure:\n\n{file_list}\n\nProposed organization:"
        payload = {
            "model": "mixtral-8x7b-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get("max_tokens"),
            "temperature": config.get("temperature")
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()["choices"][0]["message"]["content"].strip()

class BingBackend(AIBackend):
    def __init__(self):
        self.api_url = config.get("bing_endpoint")
        self.headers = {
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": config.get("bing_api_key")
        }

    def get_organization_suggestions(self, file_list):
        prompt = f"Analyze the following list of files and suggest an efficient organization structure:\n\n{file_list}\n\nProposed organization:"
        payload = {
            "messages": [
                {"role": "system", "content": "You are an AI assistant that helps organize files."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": config.get("max_tokens"),
            "temperature": config.get("temperature")
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()["choices"][0]["message"]["content"].strip()

def get_ai_backend():
    backend_type = config.get("ai_backend")
    if backend_type == "openai":
        return OpenAIBackend()
    elif backend_type == "huggingface":
        return HuggingFaceBackend()
    elif backend_type == "local":
        return LocalModelBackend()
    elif backend_type == "perplexity":
        return PerplexityBackend()
    elif backend_type == "bing":
        return BingBackend()
    else:
        raise ValueError(f"Unknown AI backend: {backend_type}")