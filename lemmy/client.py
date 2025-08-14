from __future__ import annotations

import os
import requests
from typing import Any, Dict, Iterator, List, Optional


class OpenAIClient:
    def __init__(self, api_base: str) -> None:
        self.api_base = api_base.rstrip("/")
        self.api_url = self.api_base + "/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            
        }

    def _apply_options(self, payload: Dict[str, Any], options: Dict[str, Any]) -> None:
        if not options:
            return
        if (temp := options.get("temperature")) is not None:
            payload["temperature"] = temp
        if (top_p := options.get("top_p")) is not None:
            payload["top_p"] = top_p
        if (rp := options.get("repeat_penalty")) is not None:
            payload["frequency_penalty"] = rp

    def chat(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        options: Dict[str, Any],
        stream: bool = False,
        timeout: int = 360,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
    ) -> str:
        payload: Dict[str, Any] = {"model": model, "messages": messages, "stream": stream}
        self._apply_options(payload, options)
        if tools:
            payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice

        response = requests.post(
            self.api_url, json=payload, headers=self.headers, timeout=timeout
        )
        response.encoding = "utf-8"
        response.raise_for_status()
        data = response.json()
        text = data["choices"][0]["message"].get("content") or ""
        return text.strip()

    def chat_stream(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        options: Dict[str, Any],
        timeout: int = 360,
    ) -> Iterator[str]:
        import json

        payload = {"model": model, "messages": messages, "stream": True}
        self._apply_options(payload, options)
        with requests.post(
            self.api_url,
            json=payload,
            headers=self.headers,
            timeout=timeout,
            stream=True,
        ) as resp:
            resp.encoding = "utf-8"
            resp.raise_for_status()
            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                content = line[len("data:") :].strip()
                if content == "[DONE]":
                    break
                obj = json.loads(content)
                delta = obj.get("choices", [{}])[0].get("delta", {})
                chunk = delta.get("content")
                if chunk:
                    yield chunk

    def chat_with_tools(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        options: Dict[str, Any],
        tools: List[Dict[str, Any]],
        tool_choice: Optional[str] = "auto",
        timeout: int = 360,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"model": model, "messages": messages, "stream": False, "tools": tools}
        self._apply_options(payload, options)
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice

        response = requests.post(
            self.api_url, json=payload, headers=self.headers, timeout=timeout
        )
        response.encoding = "utf-8"
        response.raise_for_status()
        data = response.json()
        msg = data.get("choices", [{}])[0].get("message", {})
        return {"message": msg}

    def get_models(self, timeout: int = 30) -> Dict[str, str]:
        models_url = self.api_base + "/models"
        try:
            response = requests.get(models_url, headers=self.headers, timeout=timeout)
            response.encoding = "utf-8"
            response.raise_for_status()
            data = response.json()
            models: Dict[str, str] = {}
            for info in data.get("data", []):
                model_id = info.get("id")
                if model_id:
                    models[model_id] = model_id
            return models
        except Exception:
            return {}
