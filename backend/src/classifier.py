import requests
import re
import os

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral:instruct"
PROMPTS_DIR = "prompts"

def load_prompt_file(filename):
    path = os.path.join(PROMPTS_DIR, filename)
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

PROMPT_ANALYZER = load_prompt_file("prompt_analyzer.txt")

def classify_email(text):
    """
    Classifica o email como 'produtivo' ou 'improdutivo' usando IA do Ollama,
    considerando apenas situações relevantes para o setor financeiro,
    utilizando o prompt de prompts/prompt_analyzer.txt.
    """
    prompt = PROMPT_ANALYZER.replace("{text}", text)
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0, "num_predict": 20}
            },
            timeout=60
        )
        if response.status_code == 200:
            raw = response.json().get("response", "").strip().lower()
            match = re.search(r"\b(produtivo|improdutivo)\b", raw)
            if match:
                return match.group(1)
        return "produtivo"
    except Exception as e:
        print(f"Erro IA classificação: {e}")
        return "produtivo"