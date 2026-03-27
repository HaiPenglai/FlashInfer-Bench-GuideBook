#!/usr/bin/env python3
"""
Claude API 测试 (api123.icu)
模型: claude-sonnet-4-6
"""

import requests

API_KEY = "sk-fb8X8N7BMB1C63CJry15ISPIKgmZgtw7ME11GrkRIrg0eSCU"
URL = "https://api123.icu/v1/chat/completions"

def ask(question):
    resp = requests.post(URL, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }, json={
        "model": "claude-sonnet-4-6",
        "messages": [{"role": "user", "content": question}],
        "max_tokens": 500
    }, timeout=30)
    return resp.json()["choices"][0]["message"]["content"]

# 测试
if __name__ == "__main__":
    print(ask("你好！请介绍一下自己。"))
