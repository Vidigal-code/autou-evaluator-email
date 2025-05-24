import os
import re
import requests
from dotenv import load_dotenv

# ------------------ CONFIG ------------------
load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:instruct")
TIMEOUT = 60  # segundos

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
PROMPT_PATH = os.path.join(PROJECT_ROOT, 'prompts', 'prompt_analyzer.txt')


# ------------------ SRP: Prompt Loader ------------------
class PromptLoader:
    @staticmethod
    def load(path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Prompt não encontrado: {os.path.abspath(path)}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


# ------------------ SRP: Request Service ------------------
class OllamaClient:
    def __init__(self, url=OLLAMA_URL, model=OLLAMA_MODEL, timeout=TIMEOUT):
        self.url = url
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.0, "num_predict": 10}
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("response", "").strip().lower()
        except requests.RequestException as e:
            print(f"[OllamaClient] Erro na requisição: {e}")
            return ""


# ------------------ SRP: Classifier ------------------
class EmailClassifier:
    def __init__(self, client: OllamaClient, prompt_template: str):
        self.client = client
        self.prompt_template = prompt_template

    def classify(self, text: str) -> str:
        if not text or not text.strip():
            print("[EmailClassifier] Texto vazio para análise.")
            return "improdutivo"

        prompt = self.prompt_template.replace("{text}", text.strip())
        raw = self.client.generate(prompt)

        if raw in ["produtivo", "improdutivo"]:
            return raw

        match = re.search(r"\b(produtivo|improdutivo)\b", raw)
        return match.group(1) if match else "improdutivo"


# ------------------ INTERFACE FINAL ------------------
# Inicialização única (uso em produção)
try:
    prompt_template = PromptLoader.load(PROMPT_PATH)
except Exception as e:
    print(f"[PromptLoader] Erro ao carregar prompt: {e}")
    prompt_template = "Classifique o seguinte texto como produtivo ou improdutivo: {text}"

_ollama_client = OllamaClient()
_email_classifier = EmailClassifier(_ollama_client, prompt_template)

def classify_email(text: str) -> str:
    return _email_classifier.classify(text)
