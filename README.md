vela/
├── api/                 # API Gateway (FastAPI + WebSocket)
├── core/                # Multi-Agent System (LangGraph)
├── mcp/                 # MCP Protocol Layer
├── edge/                # Edge Computing Engine
├── web/                 # Next.js Frontend
├── mobile/              # React Native
├── shared/              # Shared config, protocols
├── skills/              # Skill packages (user-installable)
├── data/                # Local storage
├── run.py               # Entry point
├── requirements.txt     # Python dependencies
└── ARCHITECTURE.md      # This file

## Quick Start

```bash
cd vela/

# Backend
pip install -r requirements.txt
python run.py

# Web frontend (separate terminal)
cd web && npm install && npm run dev
```

## Environment Variables
Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `LLM_DEFAULT_MODEL` | Default LLM model | `gpt-4o` |
| `OLLAMA_BASE_URL` | Ollama endpoint | `http://localhost:11434` |
| `REDIS_URL` | Redis endpoint | `redis://localhost:6379/0` |
