import os
import logging
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
HUGGINGFACE_URL = "https://api-inference.huggingface.co/models/Qwen-3-4B-GGUF"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

def query_hf_api(prompt, max_length=512):
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_length}}
    response = requests.post(HUGGINGFACE_URL, headers=HEADERS, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()[0]["generated_text"]
    
