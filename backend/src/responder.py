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

PROMPT_INITIAL = load_prompt_file("prompt_initial.txt")
PRODUCTIVE_MESSAGE = load_prompt_file("productive_message.txt")
UNPRODUCTIVE_MESSAGE = load_prompt_file("unproductive_message.txt")
MESSAGE_ERROR_IA = load_prompt_file("message_error_ia.txt")
PROMPT_SUPPORT = load_prompt_file("prompt_support.txt")

def generate_response(text, categoria):
    """
    Gera resposta automática usando IA do Ollama,
    sempre no contexto de atendimento ao cliente de uma empresa do setor financeiro.
    Retorna UMA resposta da IA + resposta padrão (do arquivo) + suporte, separados por vírgula.
    Se ocorrer erro, adiciona mensagem de erro ao resultado final.
    """
    prompt = (
        f"{PROMPT_INITIAL}\n"
        f"O e-mail abaixo foi classificado como '{categoria}'.\n"
        "Responda SOMENTE com o texto da resposta cordial em português do Brasil, pronta para ser enviada ao cliente.\n"
        "NÃO INCLUA explicações, raciocínios, etapas, comentários, tags ou instruções. Apenas escreva diretamente a resposta ao cliente, considerando o contexto de uma instituição financeira.\n\n"
        f"E-mail:\n{text}\n\nResposta:"
    )
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

    if categoria == 'produtivo':
        default_response = PRODUCTIVE_MESSAGE or "Agradecemos seu contato! Sua solicitação foi recebida pelo setor financeiro e será analisada. Em breve retornaremos com mais informações."
    else:
        default_response = UNPRODUCTIVE_MESSAGE or "Agradecemos sua mensagem! Se precisar de suporte financeiro, estamos à disposição em nossos canais oficiais."

    if not ia_response:
        ia_response = MESSAGE_ERROR_IA or "(Não foi possível gerar resposta automática pela IA)"

    # Junta tudo, separando por vírgula
    respostas = [ia_response, default_response]
    if PROMPT_SUPPORT:
        respostas.append(PROMPT_SUPPORT)
    # Adiciona mensagem de erro, se houver (útil para debug/log)
    if error_message:
        respostas.append(f"Erro: {error_message}")

    return ", ".join(respostas)

def clean_response(raw_text):
    """
    Remove tags e retorna todo o texto em português (não só a primeira linha).
    Limita só se a resposta for MUITO longa (> 1200 caracteres).
    """
    cleaned = re.sub(r'<.*?>', '', raw_text, flags=re.DOTALL)
    lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
    if not lines:
        return ""
    full_text = '\n'.join(lines)
    if len(full_text) > 1200:
        full_text = full_text[:1200] + "..."
    return full_text