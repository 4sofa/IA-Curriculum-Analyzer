# Analise de Curriculo com IA

Aplicacao web full-stack para upload de curriculos em PDF/DOCX, comparacao com uma descricao de vaga e geracao de feedback tecnico usando IA via OpenRouter.

## Sumario

- [Visao geral](#visao-geral)
- [Funcionalidades](#funcionalidades)
- [Stack](#stack)
- [Arquitetura](#arquitetura)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Requisitos](#requisitos)
- [Configuracao](#configuracao)
- [Como executar](#como-executar)
- [API](#api)
- [Seguranca](#seguranca)
- [Limites configuraveis](#limites-configuraveis)
- [Testes manuais](#testes-manuais)
- [Troubleshooting](#troubleshooting)
- [Checklist para publicar no GitHub](#checklist-para-publicar-no-github)

## Visao geral

O sistema permite que o usuario envie um curriculo, cole a descricao de uma vaga e receba uma analise estruturada em Markdown com:

- nota de aderencia;
- pontos fortes do candidato;
- lacunas em relacao a vaga;
- sugestoes praticas para melhorar o curriculo.

A chave da API do OpenRouter fica exclusivamente no backend. O frontend nunca chama o provedor de IA diretamente.

## Funcionalidades

- Upload de curriculo com validacao para `.pdf` e `.docx`.
- Interface responsiva com HTML, Tailwind CSS via CDN e JavaScript puro.
- Area obrigatoria para descricao da vaga.
- Estado de carregamento durante a analise.
- Renderizacao de resposta em Markdown.
- Sanitizacao do HTML gerado a partir do Markdown com DOMPurify.
- Extracao de texto de PDF com `pypdf`.
- Extracao de texto de DOCX com `python-docx`.
- Integracao backend com OpenRouter Chat Completions.
- Tratamento padronizado de erros.
- Endpoint de diagnostico para testar chave/modelo do OpenRouter.

## Stack

### Backend

- Python 3.11+
- FastAPI
- Uvicorn
- httpx
- python-dotenv
- python-multipart
- pypdf
- python-docx

### Frontend

- HTML
- CSS
- JavaScript
- Tailwind CSS via CDN
- marked via CDN
- DOMPurify via CDN

### IA

- OpenRouter Chat Completions
- Modelo padrao: `openrouter/free`

## Arquitetura

Fluxo principal:

```text
Usuario
  |
  | upload PDF/DOCX + descricao da vaga
  v
Frontend estatico
  |
  | POST /api/analyses
  v
FastAPI backend
  |
  | valida arquivo, tamanho e descricao
  v
Extrator de texto
  |
  | texto puro do curriculo
  v
OpenRouter client
  |
  | prompt estruturado + dados do curriculo/vaga
  v
OpenRouter API
  |
  | Markdown da analise
  v
Frontend renderiza resultado sanitizado
```

Principais decisoes:

- Backend e frontend ficam no mesmo servidor FastAPI para simplificar execucao local.
- A API usa `multipart/form-data` para receber arquivo e texto da vaga.
- O prompt instrui o modelo a tratar curriculo e vaga como dados nao confiaveis.
- O payload enviado ao OpenRouter usa `reasoning: {"exclude": true}` para evitar respostas vazias em modelos que retornam apenas raciocinio.

## Estrutura do projeto

```text
resume-ai-analyzer/
|-- app/
|   |-- __init__.py
|   |-- main.py
|   |-- core/
|   |   |-- __init__.py
|   |   |-- config.py
|   |   `-- errors.py
|   |-- routes/
|   |   |-- __init__.py
|   |   `-- analyses.py
|   `-- services/
|       |-- __init__.py
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

## Requisitos

- Python 3.11 ou superior.
- Uma chave de API do OpenRouter.
- Navegador moderno.

Verifique o Python:

```powershell
python --version
```

No Windows, se o comando abrir a Microsoft Store ou nao mostrar uma versao real, instale o Python pelo site oficial e marque a opcao para adicionar ao PATH.

## Configuracao

Clone o repositorio e entre na pasta:

```powershell
git clone https://github.com/seu-usuario/resume-ai-analyzer.git
cd resume-ai-analyzer
```

Crie o ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Se o PowerShell bloquear a ativacao:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Crie o arquivo `.env`:

```powershell
Copy-Item .env.example .env
```

Edite `.env`:

```env
OPENROUTER_API_KEY=sk-or-sua-chave-aqui
OPENROUTER_MODEL=openrouter/free
OPENROUTER_APP_URL=http://localhost:8000
OPENROUTER_APP_NAME=Analise de Curriculo com IA
OPENROUTER_MAX_COMPLETION_TOKENS=4096

MAX_UPLOAD_BYTES=8388608
MAX_PDF_PAGES=40
MAX_RESUME_CHARS=40000
MAX_JOB_DESCRIPTION_CHARS=20000
MIN_JOB_DESCRIPTION_CHARS=20
```

## Como executar

Com a venv ativa:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Acesse:

```text
http://127.0.0.1:8000
```

## API

### `GET /`

Serve a interface web principal.

### `GET /api/health`

Verifica se a API esta viva.

Resposta:

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "model": "openrouter/free"
  }
}
```

### `GET /api/ready`

Verifica se a chave do OpenRouter foi carregada, sem retornar o valor da chave.

Resposta:

```json
{
  "success": true,
  "data": {
    "status": "ready",
    "has_openrouter_api_key": true
  }
}
```

### `GET /api/openrouter-test`

Faz uma chamada minima ao OpenRouter para validar chave, creditos, conectividade e modelo.

Resposta:

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "model": "openrouter/free",
    "response": "ok"
  }
}
```

### `POST /api/analyses`

Analisa um curriculo em relacao a uma vaga.

Content-Type:

```text
multipart/form-data
```

Campos:

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---:|---|
| `resume` | arquivo | Sim | Curriculo em `.pdf` ou `.docx`. |
| `job_description` | texto | Sim | Descricao da vaga. |

Exemplo com `curl.exe` no PowerShell:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/analyses" `
  -F "resume=@C:\caminho\para\curriculo.pdf" `
  -F "job_description=Desenvolvedor Python com experiencia em FastAPI, APIs REST, integracoes com IA e boas praticas de seguranca."
```

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
    "details": {
      "allowed_extensions": [".docx", ".pdf"]
    }
  }
}
```

## Seguranca

- `.env` esta no `.gitignore` e nao deve ser enviado ao GitHub.
- A chave `OPENROUTER_API_KEY` e lida apenas pelo backend.
- O frontend chama somente rotas locais da FastAPI.
- O backend valida extensao e assinatura basica do arquivo.
- PDFs criptografados sao rejeitados.
- PDFs com paginas demais sao rejeitados.
- Arquivos vazios ou grandes demais sao rejeitados.
- O prompt instrui o modelo a ignorar tentativas de prompt injection vindas do curriculo ou da vaga.
- A resposta Markdown e sanitizada no frontend com DOMPurify.
- Erros internos nao retornam stack trace.
- Erros do OpenRouter retornam status e mensagem segura, sem expor credenciais.

## Limites configuraveis

| Variavel | Padrao | Descricao |
|---|---:|---|
| `OPENROUTER_MODEL` | `openrouter/free` | Modelo ou roteador usado no OpenRouter. |
| `OPENROUTER_MAX_COMPLETION_TOKENS` | `4096` | Limite de tokens de saida da IA. |
| `MAX_UPLOAD_BYTES` | `8388608` | Tamanho maximo do arquivo, em bytes. |
| `MAX_PDF_PAGES` | `40` | Numero maximo de paginas em PDFs. |
| `MAX_RESUME_CHARS` | `40000` | Maximo de caracteres do curriculo enviados ao modelo. |
| `MAX_JOB_DESCRIPTION_CHARS` | `20000` | Maximo de caracteres da descricao da vaga. |
| `MIN_JOB_DESCRIPTION_CHARS` | `20` | Minimo de caracteres para aceitar a vaga. |

## Testes manuais

Com o servidor rodando:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
Invoke-RestMethod http://127.0.0.1:8000/api/ready
Invoke-RestMethod http://127.0.0.1:8000/api/openrouter-test
```

Teste pela interface:

1. Acesse `http://127.0.0.1:8000`.
2. Selecione um arquivo `.pdf` ou `.docx`.
3. Cole a descricao da vaga.
4. Clique em `Analisar Curriculo`.
5. Verifique se a resposta aparece formatada na area de resultado.

## Troubleshooting

### `OPENROUTER_API_KEY` nao configurada

Crie `.env` e defina:

```env
OPENROUTER_API_KEY=sk-or-sua-chave-aqui
```

Depois reinicie o `uvicorn`.

### OpenRouter retorna `401`

A chave esta ausente, invalida ou foi copiada com espacos extras.

### OpenRouter retorna `402`

A conta pode estar sem creditos ou com restricao de pagamento.

### OpenRouter retorna `404`

O valor de `OPENROUTER_MODEL` nao foi encontrado. O padrao deste projeto e:

```env
OPENROUTER_MODEL=openrouter/free
```

### OpenRouter retorna resposta vazia

Alguns modelos retornam raciocinio separado de `content`. O backend ja envia:

```json
{
  "reasoning": {
    "exclude": true
  }
}
```

Se ainda ocorrer, aumente:

```env
OPENROUTER_MAX_COMPLETION_TOKENS=4096
```

### PDF sem texto

PDFs escaneados como imagem podem nao ter texto extraivel. Este projeto nao faz OCR.

### Erro ao ativar venv no PowerShell

Execute:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Checklist para publicar no GitHub

Antes de fazer upload:

- Confirme que `.env` nao sera enviado.
- Confirme que `.venv/` nao sera enviado.
- Confirme que `__pycache__/` nao sera enviado.
- Use `.env.example` como exemplo publico de configuracao.
- Remova curriculos reais ou arquivos com dados pessoais.
- Rode o projeto localmente pelo menos uma vez.

Comandos sugeridos:

```powershell
git init
git add .
git status
git commit -m "Initial resume AI analyzer app"
git branch -M main
git remote add origin https://github.com/seu-usuario/resume-ai-analyzer.git
git push -u origin main
```

## Observacoes de privacidade

Curriculos contem dados pessoais. Antes de usar esta aplicacao com documentos reais, garanta que o usuario autorizou o envio do texto extraido para um provedor externo de IA.

## Licenca

Defina uma licenca antes de publicar o repositorio. Para projetos abertos, uma opcao comum e `MIT`.
