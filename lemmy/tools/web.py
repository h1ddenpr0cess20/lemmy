from __future__ import annotations

from typing import Any, Dict

import requests


def fetch_url(url: str, max_bytes: int = 65536) -> Dict[str, Any]:
    """Fetch text content from a URL, truncating to max_bytes."""
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        text = resp.text
        encoded = text.encode("utf-8")
        truncated = False
        if len(encoded) > max_bytes:
            text = encoded[:max_bytes].decode("utf-8", errors="ignore")
            truncated = True
        return {
            "url": url,
            "status": resp.status_code,
            "content": text,
            "truncated": truncated,
        }
    except requests.RequestException as e:
        return {"error": f"Request failed: {e}"}

"""
disabling for now, here's the schema

{
    "type": "function",
    "function": {
      "name": "fetch_url",
      "description": "Fetch text content from an HTTP(S) URL.",
      "parameters": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string",
            "description": "The URL to retrieve."
          },
          "max_bytes": {
            "type": "integer",
            "description": "Maximum number of bytes to return (default 65536)."
          }
        },
        "required": ["url"],
        "additionalProperties": false
      }
    }
  }

"""