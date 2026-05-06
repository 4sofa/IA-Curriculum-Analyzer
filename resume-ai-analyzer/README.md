# Analise de Curriculo com IA

Aplicacao web local para enviar um curriculo em PDF ou DOCX, colar a descricao de uma vaga e receber uma analise em Markdown gerada via OpenRouter.

## Estrutura

```text
resume-ai-analyzer/
|-- app/
|   |-- main.py
|   |-- core/
|   |   |-- config.py
|   |   `-- errors.py
|   |-- routes/
|   |   `-- analyses.py
|   `-- services/
|       |-- document_extractor.py
|       `-- openrouter_client.py
|-- static/
|   |-- index.html
|   |-- styles.css
|   `-- app.js
|-- .env.example
|-- .gitignore
|-- DESIGN.md
|-- README.md
`-- requirements.txt
```

## Stack

- Backend: FastAPI
- Extracao de PDF: pypdf
- Extracao de DOCX: python-docx
- Cliente HTTP: httpx
- Configuracao local: python-dotenv
- Frontend: HTML, Tailwind CSS via CDN e Fetch API
- Markdown: marked + DOMPurify via CDN
- IA: OpenRouter Chat Completions

## Instalar

Pre-requisito: Python 3.11+ instalado e disponivel no PATH. Se `python --version` abrir a Microsoft Store ou nao mostrar uma versao real, instale pelo site oficial do Python e marque a opcao de adicionar ao PATH.

No Windows PowerShell, a partir desta pasta:

```powershell
cd "C:\Users\Gustavo-SOFA\Documents\Nova pasta\resume-ai-analyzer"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Se o PowerShell bloquear a ativacao da venv:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Configurar

Crie o arquivo `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Edite `.env` e informe sua chave:

```env
OPENROUTER_API_KEY=sk-or-sua-chave-aqui
OPENROUTER_MODEL=openrouter/free
OPENROUTER_APP_URL=http://localhost:8000
OPENROUTER_APP_NAME=Analise de Curriculo com IA
OPENROUTER_MAX_COMPLETION_TOKENS=4096
```

A chave fica apenas no backend. O frontend chama a rota local `/api/analyses`, nunca o OpenRouter diretamente.

## Rodar

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Acesse:

```text
http://127.0.0.1:8000
```

## Endpoints

- `GET /api/health`: verifica se a API esta viva.
- `GET /api/ready`: verifica se a chave do OpenRouter foi carregada, sem expor o valor.
- `GET /api/openrouter-test`: faz uma chamada minima ao OpenRouter para validar chave, creditos e modelo.
- `POST /api/analyses`: recebe `multipart/form-data` com:
  - `resume`: arquivo `.pdf` ou `.docx`
  - `job_description`: descricao obrigatoria da vaga

Resposta de sucesso:

```json
{
  "success": true,
  "data": {
    "analysis": "# Analise do Curriculo\n...",
    "model": "openrouter/free",
    "filename": "curriculo.pdf",
    "resume_characters": 12000,
    "resume_truncated": false
  }
}
```

Resposta de erro:

```json
{
  "success": false,
  "error": {
    "code": "unsupported_file_type",
    "message": "Envie um arquivo .pdf ou .docx.",
    "details": {}
  }
}
```

## Testes rapidos

API viva:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

Prontidao da chave:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/ready
```

Teste direto do OpenRouter:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/openrouter-test
```

Upload via PowerShell:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/analyses" `
  -F "resume=@C:\caminho\para\curriculo.pdf" `
  -F "job_description=Desenvolvedor Python com experiencia em FastAPI, APIs REST, integracoes com IA e boas praticas de seguranca."
```

## Seguranca e limites

- `.env` esta no `.gitignore`.
- Somente `.pdf` e `.docx` sao aceitos.
- O backend valida extensao, assinatura basica do arquivo, tamanho, PDF criptografado e numero maximo de paginas.
- Curriculo e descricao da vaga sao tratados como dados nao confiaveis no prompt.
- O frontend sanitiza o Markdown renderizado com DOMPurify.
- Erros retornam mensagens claras sem expor stack trace ou chave de API.

## Referencias

- OpenRouter Chat Completions: https://openrouter.ai/docs/api-reference/chat-completion
- Modelo usado: `openrouter/free`
