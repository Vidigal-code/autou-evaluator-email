import os
import re
import requests
from dotenv import load_dotenv

# ------------------ CONFIG ------------------
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:instruct")
TIMEOUT = 60

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
PROMPTS_DIR = os.path.join(PROJECT_ROOT, "prompts")

# ------------------ SRP: FileLoader ------------------
class FileLoader:
    @staticmethod
    def load(filename):
        path = os.path.join(PROMPTS_DIR, filename)
        if not os.path.isfile(path):
            print(f"[FileLoader] Arquivo não encontrado: {os.path.abspath(path)}")
            return ""
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()


# ------------------ SRP: OllamaClient ------------------
class OllamaClient:
    def __init__(self, url=OLLAMA_URL, model=OLLAMA_MODEL, timeout=TIMEOUT):
        self.url = url
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str, temperature=0.5, num_predict=200) -> str:
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": num_predict}
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.RequestException as e:
            raise RuntimeError(f"Erro na requisição IA: {e}")


# ------------------ SRP: TextCleaner ------------------
class TextCleaner:
    @staticmethod
    def clean(text: str, max_length=1200) -> str:
        cleaned = re.sub(r'<.*?>', '', text, flags=re.DOTALL)
        cleaned = re.sub(r'\[.*?\]|\{.*?\}|\(.*?\)', '', cleaned)
        cleaned = re.sub(
            r'(?i)(atenciosamente|cordialmente|equipe financeira|equipe de atendimento|suporte financeiro|empresa xyz|nome da empresa|função|cargo).*',
            '', cleaned
        )
        lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
        full_text = '\n'.join(lines)
        return (full_text[:max_length] + "...") if len(full_text) > max_length else full_text


# ------------------ SRP: SupportDetector ------------------
class SupportDetector:
    def __init__(self, keywords):
        self.keywords = [k.lower() for k in keywords]

    def requested(self, text):
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.keywords)


# ------------------ SRP: Responder ------------------
class EmailResponder:
    def __init__(self, client: OllamaClient, prompts: dict, support_detector: SupportDetector):
        self.client = client
        self.prompts = prompts
        self.support_detector = support_detector

    def respond(self, text: str, category: str) -> str:
        prompt = f"{self.prompts['initial']}\nE-mail do cliente:\n{text}\nResposta:"
        try:
            raw_response = self.client.generate(prompt)
            ia_response = TextCleaner.clean(raw_response)
        except Exception as e:
            print(f"[EmailResponder] Erro IA: {e}")
            ia_response = self.prompts['error_ia']
            error_message = str(e)
        else:
            error_message = None

        default_msg = (
            self.prompts['productive'] if category == 'produtivo'
            else self.prompts['unproductive']
        )

        responses = [ia_response or self.prompts['error_ia'], default_msg]

        if self.support_detector.requested(text) and self.prompts.get('support'):
            responses.append(self.prompts['support'])

        if error_message:
            responses.append(f"Erro: {error_message}")

        return ", ".join(responses)
