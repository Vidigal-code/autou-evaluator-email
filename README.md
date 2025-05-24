# Classificador de E-mails AutoU 🚀

Este projeto é uma solução prática para classificação automática de e-mails e sugestão de respostas, utilizando **Inteligência Artificial open-source** (Ollama com o modelo `mistral:instruct`) e técnicas de NLP. Ele foi desenvolvido como parte do desafio da AutoU e está pronto para deploy, uso local, apresentação e avaliação.

---

## ✨ Funcionalidades

- **Upload de e-mails** em `.txt` ou `.pdf` ou colagem direta do texto.
- **Classificação automática** em _Produtivo_ ou _Improdutivo_ usando IA.
- **Resposta automática gerada pela IA** em português, cordial e pronta para envio ao cliente.
- **Pré-processamento NLP** com NLTK: stemming, stopwords etc.
- **Interface web responsiva** (HTML, CSS, JS), modo claro/escuro, UX amigável.
- **Backend Python/Flask** simples e robusto.
- **Deploy-ready** para nuvem (Railway, Heroku, Render, etc.)

---

## 📸 Demonstração (Workflow)

1. **Acesse a interface web**.
2. Faça upload de um `.txt` ou `.pdf` de e-mail **ou cole o texto**.
3. Clique em **Enviar**.
4. Veja:
   - **Categoria:** _Produtivo_ ou _Improdutivo_
   - **Resposta sugerida:** Pronta para copiar/usar
   - **Prévia do texto processado**

---

## 🚀 Como rodar localmente

### 1. Requisitos

- **Python 3.9+**
- **[Ollama](https://ollama.com/download) instalado e rodando localmente**
- Modelo `mistral:instruct` baixado no Ollama:
  ```sh
  ollama pull mistral:instruct
  ollama serve
  ```
- Dependências Python:
  ```
  pip install -r backend/requirements.txt
  ```
  (inclui `flask`, `requests`, `flask-cors`, `pdfplumber`, `nltk`)

### 2. Estrutura de Pastas

```
backend/
   requirements.txt
  app.py
  src/
    classifier.py
    responder.py
    utils.py
    
frontend/
  index.html
  main.js
  style.css
README.md
```

### 3. Rodando o backend

No diretório `backend/`:

```sh
python app.py

or

python backend/app.py

```

O backend Flask rodará por padrão em `http://localhost:5000/`.

### 4. Rodando o frontend

Acesse `http://localhost:5000/` no navegador.

---

## ☁️ Deploy na nuvem

Você pode fazer deploy facilmente em [Railway](https://railway.app/), [Render](https://render.com/), [Heroku](https://heroku.com/) etc.

- **Importante:** O Ollama precisa estar rodando em um servidor com suporte a containers ou VMs. Em ambientes gratuitos, pode ser necessário adaptar para usar uma API de LLM externa.
- O frontend pode ser hospedado em Vercel, Netlify, ou na própria pasta `frontend` do Flask.

---

## 🧠 Decisões técnicas

- **Modelo IA:** `mistral:instruct` via [Ollama](https://ollama.com/). Leve, open-source e com desempenho adequado para classificação binária e respostas em português.
- **NLP:** NLTK para pré-processamento (stopwords, stemming), facilitando futuras expansões.
- **Prompt engineering:** Prompts explícitos e robustos, evitando respostas ambíguas da IA.
- **Fallbacks:** Resposta padrão amigável caso a IA falhe.

---

## 📝 Como testar

- Faça upload de um arquivo `.txt` ou `.pdf` com um e-mail, ou cole o texto no campo correspondente.
- Clique em **Enviar**.
- Veja a classificação e a resposta sugerida.

---

## 📦 Dependências

```
flask
flask-cors
werkzeug
pdfplumber
nltk
requests
```

---
## 📹 Vídeo Demonstrativo

Confira o vídeo demonstrativo:

- [Youtube](https://www.youtube.com/watch?v=QMO2L-pq_X4&ab_channel=KauanVidigal)



## 🤝 Contato

Dúvidas, feedbacks ou sugestões?  
Entre em contato: **[Kauan Vidigal]** • [kauanvidigalcontato@gmail.com]

---

## 🎉 Observações finais

- O projeto está pronto para ser testado por usuários leigos e técnicos.
- O código é limpo, modular e fácil de adaptar.
- Sinta-se à vontade para sugerir melhorias ou expandir o projeto!

---

> **AutoU Case Prático — Solução por [Kauan Vidigal] - Github [https://github.com/Vidigal-code]**
