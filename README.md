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
  .env
  src/
    classifier.py
    responder.py
    utils.py
  tests/
   test_classifier.py
   test_responder.py
    
frontend/
  index.html
  main.js
  style.css
README.md
```

### 3. Configuração do arquivo `.env`

O backend utiliza variáveis de ambiente para configurar a integração com o Ollama.  
**Crie um arquivo chamado `.env` na raiz do projeto (ou dentro da pasta `backend/` se desejar) com o seguinte conteúdo:**

```env
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral:instruct
```

- `OLLAMA_URL`: Endereço local da API do Ollama (padrão para instalação local).
- `OLLAMA_MODEL`: Nome do modelo baixado no Ollama.

Se quiser usar outro modelo ou um servidor Ollama remoto, basta alterar esses valores no `.env`, sem necessidade de alterar o código.

### 4. Rodando o backend

No diretório `backend/`:

```sh
python app.py

or

python backend/app.py

```

O backend Flask rodará por padrão em `http://localhost:5000/`.

### 5. Rodando o frontend

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
python-dotenv
pytest
```

---

## 🧪 Testes automatizados com pytest

O projeto já vem com testes automatizados utilizando o [pytest](https://docs.pytest.org/) para garantir a qualidade e o funcionamento dos principais módulos do backend.

### Como rodar os testes

1. Certifique-se de que as dependências estão instaladas:
   ```
   pip install -r backend/requirements.txt
   ```

2. Navegue até a pasta do backend:
   ```
   cd backend
   ```

3. Execute o pytest:
   ```
   pytest
   ```

   Você verá uma saída parecida com:
   ```
   collected 3 items

   tests/test_classifier.py ..                                                                                      [ 66%]
   tests/test_responder.py .                                                                                        [100%]

   ================================================== 3 passed in 0.87s ==================================================
   ```

   - Os pontos `.` indicam testes que passaram.
   - O progresso (`[ 66%]`, `[100%]`) mostra o andamento da execução.
   - Se todos os testes passaram, está tudo certo!

### Estrutura dos testes

- Os testes estão no diretório `backend/tests/`.
- Cada arquivo testa um módulo específico, por exemplo:
  - `test_classifier.py` testa a classificação de e-mails.
  - `test_responder.py` testa a limpeza e preparação de respostas automáticas.

### Observações sobre dependências externas

- Os testes de classificação dependem do Ollama estar rodando e do modelo carregado. Para garantir testes consistentes e independentes, recomenda-se utilizar mocks nas funções que fazem chamadas externas (exemplo no próprio código de teste).
- Se algum teste falhar, verifique se o Ollama está ativo e o modelo correto está disponível, ou utilize mocks conforme exemplo comentado nos arquivos de teste.

### Mais informações

- Para saber mais sobre pytest, consulte [a documentação oficial](https://docs.pytest.org/).

---

## 📹 Vídeo Demonstrativo

Confira o vídeo demonstrativo:

- [Youtube - 1](https://www.youtube.com/watch?v=QMO2L-pq_X4&ab_channel=KauanVidigal)
- [Youtube - 2](https://www.youtube.com/watch?v=bMJZEQ9ocEU)

---

## 🗂️ Exemplos de arquivos `.env`

```env
# Exemplo de .env para rodar localmente
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral:instruct
```

> **Dica:** Nunca suba o arquivo `.env` para repositórios públicos!

---

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