import requests  
import re
import os
from dotenv import load_dotenv
try:
    import requests
except ImportError:
    print("O módulo 'requests' não está instalado. Execute 'pip install requests' para instalá-lo.")
    raise
# Carrega variáveis do arquivo .env
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:instruct")
TIMEOUT = 60  # segundos

# Caminho da raiz do projeto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# Caminho para o arquivo de prompt
PROMPT_PATH = os.path.join(PROJECT_ROOT, 'prompts', 'prompt_analyzer.txt')

def load_prompt_file(path):
    if not os.path.isfile(path):
        print(f"Arquivo não encontrado: {os.path.abspath(path)}")
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

PROMPT_ANALYZER = load_prompt_file(PROMPT_PATH)

def classify_email(text):
    if not text or not text.strip():
        print("Erro: texto para análise está vazio.")
        return "improdutivo"

    # Substitui o placeholder {text} pelo texto do e-mail
    prompt = PROMPT_ANALYZER.replace("{text}", text.strip())
    #print(repr(PROMPT_ANALYZER))

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0, "num_predict": 10}
            },
            timeout=TIMEOUT
        )
        if response.status_code == 200:
            data = response.json()
            raw = data.get("response", "").strip().lower()

            if raw == "produtivo":
                return "produtivo"
            if raw == "improdutivo":
                return "improdutivo"

            match = re.search(r"\b(produtivo|improdutivo)\b", raw)
            if match:
                return match.group(1)
            return "improdutivo"
        else:
            print(f"Erro na requisição: status {response.status_code}")
            return "improdutivo"
    except Exception as e:
        print(f"Erro IA classificação: {e}")
        return "improdutivo"