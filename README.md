# 🎥 YouTube Video Data Extractor

Aplicação Python profissional para extração completa de dados de vídeos do YouTube, incluindo Shorts. Arquitetura limpa, escalável e preparada para integração com agentes de IA.

## ✨ Funcionalidades

- ✅ **Extração de Metadados**: Título, descrição, canal, estatísticas
- 🏷️ **Hashtags**: Extração automática de hashtags da descrição
- 📝 **Transcrições**: Legendas em múltiplos idiomas (PT, EN, ES) com fallback automático
- 💬 **Comentários**: 15 comentários mais recentes ordenados por data
- 📊 **Exportação**: Suporte a JSON (simples e completo) e CSV
- 🔄 **Retry Logic**: Exponential backoff para rate limiting
- 📋 **Logging Estruturado**: JSON e texto formatado para auditoria
- 🎨 **CLI Rica**: Interface colorida com progress bars

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Chave da YouTube Data API v3

### Passos

1. **Clone ou baixe o projeto**

```bash
git clone https://github.com/juliocadelca/Agente-Extrator-Video.git

cd "Agente Extrator Vídeo"
```

2. **Crie e ative um ambiente virtual**

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

Ou usando UV (Eu prefiro):

```bash
uv init
uv venv
uv add -r requirements.txt
uv sync
```

4. **Configure a chave da API**

O arquivo `.env` já está configurado com a chave fornecida. Se necessário, edite:

```env
YOUTUBE_API_KEY=sua_chave_aqui
```

## 📖 Uso

### CLI (Interface de Linha de Comando)

**Uso básico:**

```bash
python main.py --url "https://youtube.com/watch?v=VIDEO_ID"
```

**Exportar para JSON simplificado:**

```bash
python main.py --url "https://youtube.com/shorts/VIDEO_ID" --output json --simple
```

**Exportar para CSV:**

```bash
python main.py --url "VIDEO_ID" --output csv --file dados.csv
```

**Exportar em ambos os formatos:**

```bash
python main.py --url "URL_DO_VIDEO" --output both
```

### Argumentos Disponíveis

| Argumento | Descrição | Padrão |
|-----------|-----------|--------|
| `--url` | URL do vídeo ou ID (obrigatório) | - |
| `--output` | Formato de saída: `json`, `csv`, `both` | `json` |
| `--file` | Caminho personalizado para salvar | Auto-gerado |
| `--simple` | Usar JSON simplificado (apenas campos essenciais) | `false` |
| `--version` | Mostrar versão | - |

### Como Biblioteca Python

```python
from main import get_video_data

# Extrair dados de um vídeo
resultado = get_video_data("https://youtube.com/watch?v=dQw4w9WgXcQ")

print(resultado["title"])
print(resultado["hashtags"])
print(resultado["transcript"])
print(len(resultado["recent_comments"]))
```

**Formato de retorno (simplificado):**

```json
{
    "title": "Título do Vídeo",
    "description": "Descrição completa...",
    "hashtags": ["tutorial", "python"],
    "transcript": "Transcrição completa do áudio...",
    "recent_comments": [
        {
            "author": "Nome do Autor",
            "text": "Texto do comentário",
            "published_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

## 🏗️ Arquitetura

```
Agente Extrator Vídeo/
├── src/                        # Código principal
│   ├── config.py              # Configurações validadas (Pydantic)
│   ├── data_models.py         # Modelos de dados
│   ├── url_parser.py          # Parser de URLs do YouTube
│   ├── youtube_client.py      # Cliente YouTube API v3
│   ├── transcript_service.py  # Serviço de transcrições
│   └── comments_service.py    # Serviço de comentários
├── utils/                      # Utilitários
│   ├── logger.py              # Sistema de logging
│   └── exporters.py           # Exportadores JSON/CSV
├── main.py                     # CLI principal
├── requirements.txt            # Dependências
├── .env                        # Variáveis de ambiente
└── logs/                       # Logs estruturados
```

### Princípios de Design

- **Separation of Concerns**: Cada módulo tem responsabilidade única
- **Dependency Injection**: Serviços recebem dependências via construtor
- **Error Handling**: Tratamento robusto em múltiplas camadas
- **Type Safety**: Type hints completos para melhor IDE support
- **Logging**: Auditoria completa de operações
- **Configuração**: Pydantic para validação de configurações

## 🔧 Configuração Avançada

### Variáveis de Ambiente (`.env`)

```env
# API Key (obrigatório)
YOUTUBE_API_KEY=sua_chave

# Nível de log: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Formato de log: json ou text
LOG_FORMAT=text

# Número de tentativas em caso de erro
MAX_RETRIES=3

# Delay entre tentativas (segundos)
RETRY_DELAY=2

# Idiomas de transcrição (separados por vírgula)
TRANSCRIPT_LANGUAGES=pt,en,es

# Usar legendas automáticas como fallback
TRANSCRIPT_FALLBACK=true
```

## 📊 Formatos de Saída

### JSON Simplificado (`--simple`)

Apenas campos essenciais conforme especificação:

```json
{
  "title": "...",
  "description": "...",
  "hashtags": [],
  "transcript": "",
  "recent_comments": [...]
}
```

### JSON Completo

Inclui metadados adicionais:

```json
{
  "video_id": "...",
  "title": "...",
  "description": "...",
  "hashtags": [],
  "transcript": "",
  "recent_comments": [...],
  "channel_title": "...",
  "published_at": "...",
  "duration": "PT10M30S",
  "view_count": 1000000,
  "like_count": 50000,
  "comment_count": 1500,
  "transcript_available": true,
  "comments_enabled": true,
  "extraction_timestamp": "2024-01-15T15:00:00Z"
}
```

### CSV

Formato estruturado com uma linha para cada tipo de dado:
- Linha 1: Informações do vídeo
- Linhas seguintes: Hashtags, transcrição, comentários

## 🛡️ Tratamento de Erros

A aplicação trata os seguintes cenários:

- ❌ **Vídeo não encontrado**: Mensagem clara com código 404
- 🔒 **Vídeo privado**: Detecção automática
- 💬 **Comentários desabilitados**: Continua sem falhar
- 📝 **Transcrição indisponível**: Fallback para múltiplos idiomas
- ⏱️ **Rate limiting**: Exponential backoff automático
- 🔑 **API key inválida**: Validação antes de iniciar
- 🌐 **Problemas de rede**: Retry com backoff

## 🔍 Logs

Logs são salvos em `logs/youtube_extractor.log` em formato JSON:

```json
{
  "timestamp": "2024-01-15T15:00:00Z",
  "level": "INFO",
  "logger": "youtube_extractor",
  "message": "Extração concluída com sucesso",
  "video_id": "dQw4w9WgXcQ",
  "components": {
    "metadata": true,
    "transcript": true,
    "comments": true
  }
}
```

## 🔐 Segurança

- ✅ Chaves de API em variáveis de ambiente (nunca no código)
- ✅ `.gitignore` configurado para prevenir vazamento de credenciais
- ✅ Validação de entrada (URLs e IDs)
- ✅ Rate limiting respeitado
- ✅ Logs estruturados para auditoria

## 🤖 Preparação para IA

O código está estruturado para facilitar integração com agentes de IA:

1. **Modelos Pydantic**: Estruturas de dados bem definidas
2. **Logging JSON**: Fácil parsing por agentes
3. **Separação de responsabilidades**: Fácil extração de componentes
4. **Type hints**: Melhor análise estática
5. **Documentação**: Docstrings completas

## 📝 Exemplos

### Extrair dados de um Short

```bash
python main.py --url "https://youtube.com/shorts/abc123xyz"
```

### Analisar vídeo e salvar em CSV

```bash
python main.py --url "https://youtu.be/dQw4w9WgXcQ" --output csv
```

### Processar apenas metadados (JSON simplificado)

```bash
python main.py --url "VIDEO_ID" --simple
```

## 🐛 Troubleshooting

**Erro: "Chave da API do YouTube não configurada"**
- Verifique se o arquivo `.env` existe
- Confirme que `YOUTUBE_API_KEY` está definido

**Erro: "Limite de requisições excedido"**
- A API tem quotas diárias
- Aguarde alguns minutos e tente novamente
- Aumente `RETRY_DELAY` no `.env`

**Transcrição não disponível**
- Nem todos os vídeos têm legendas
- Configure `TRANSCRIPT_LANGUAGES` para mais idiomas
- Ative `TRANSCRIPT_FALLBACK=true`

## 📄 Licença

Este projeto é fornecido como está, sem garantias. Use por sua conta e risco.

## 🤝 Contribuindo

Sugestões de melhorias são bem-vindas!

---

**Desenvolvido com ❤️ para extração profissional de dados do YouTube**
