import requests
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:instruct")

# Paths relative to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
PROMPTS_DIR = os.path.join(PROJECT_ROOT, "prompts")

def load_prompt_file(filename):
    path = os.path.join(PROMPTS_DIR, filename)
    if not os.path.isfile(path):
        print(f"Arquivo não encontrado: {os.path.abspath(path)}")
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

# Load prompts
PROMPT_INITIAL = load_prompt_file("prompt_initial.txt")
PRODUCTIVE_MESSAGE = load_prompt_file("productive_message.txt")
UNPRODUCTIVE_MESSAGE = load_prompt_file("unproductive_message.txt")
MESSAGE_ERROR_IA = load_prompt_file("message_error_ia.txt")
PROMPT_SUPPORT = load_prompt_file("prompt_support.txt")
FILTER_SUPPORT = load_prompt_file("filter_support.txt")

# Generate list of support keywords from filter file
SUPPORT_KEYWORDS = [line.strip().lower() for line in FILTER_SUPPORT.splitlines() if line.strip()]

def client_requested_support(text):
    """Returns True if the client requested support or contact channels in the text."""
    text_lower = text.lower()
    return any(word in text_lower for word in SUPPORT_KEYWORDS)

def clean_response(raw_text):
    """Removes tags, placeholders, fictitious names/positions, signatures, and brackets."""
    cleaned = re.sub(r'<.*?>', '', raw_text, flags=re.DOTALL)
    cleaned = re.sub(r'\[.*?\]|\{.*?\}|\(.*?\)', '', cleaned)
    cleaned = re.sub(
        r'(?i)(atenciosamente|cordialmente|equipe financeira|equipe de atendimento|suporte financeiro|empresa xyz|nome da empresa|função|cargo).*',
        '', cleaned
    )
    lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
    if not lines:
        return ""
    full_text = '\n'.join(lines)
    if len(full_text) > 1200:
        full_text = full_text[:1200] + "..."
    return full_text

def generate_response(text, category):
    """
    Generates automatic response using Ollama AI,
    always in the context of customer service for the financial department.
    Returns an AI response + default response + support message, separated by commas.
    If an error occurs, adds the error message to the final output.
    """
    # Build the full prompt including the client email text
    prompt = f"{PROMPT_INITIAL}\nE-mail do cliente:\n{text}\nResposta:"

    ia_response = ""
    error_message = ""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.5, "num_predict": 200}
            },
            timeout=60
        )
        if response.status_code == 200:
            raw = response.json().get("response", "").strip()
            ia_response = clean_response(raw)
        else:
            error_message = f"Erro na requisição à IA: código {response.status_code}"
    except Exception as e:
        print(f"Erro IA resposta: {e}")
        error_message = f"Erro ao conectar à IA: {str(e)}"

    if category == 'produtivo':
        default_response = PRODUCTIVE_MESSAGE or "Agradecemos seu contato! Sua solicitação foi recebida pelo setor financeiro e será analisada. Em breve retornaremos com mais informações."
    else:
        default_response = UNPRODUCTIVE_MESSAGE or "Agradecemos sua mensagem! Se precisar de suporte financeiro, estamos à disposição em nossos canais oficiais."

    if not ia_response:
        ia_response = MESSAGE_ERROR_IA or "(Não foi possível gerar resposta automática pela IA)"

    responses = [ia_response, default_response]

    if client_requested_support(text) and PROMPT_SUPPORT:
        responses.append(PROMPT_SUPPORT)

    if error_message:
        responses.append(f"Erro: {error_message}")

    return ", ".join(responses)