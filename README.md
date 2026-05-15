<div align="center">

# 🤖 Ads-Agent
### AI-Powered Advertising Pipeline using Multi-Agent Systems

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-FF6B6B?style=flat)](https://crewai.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)

**A production-grade backend system that uses 4 specialized CrewAI agents to autonomously scrape, analyse, script, and produce 60-second video ads for trading and finance brands — with zero human intervention.**

• [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Contributing](#-contributing)

</div>

---

## 🧠 What Is This?

Most ad creation workflows are slow, manual, and expensive. **Ads-Agent** replaces that entire pipeline with a crew of 4 autonomous AI agents that collaborate — each with a specialized role — to produce a complete 60-second video ad from scratch.

You give it a niche (e.g. `"trading"`). It handles everything else.

```
Input: "trading"   →   Output: final_ad_20260514.mp4
```

---

## ⚙️ Architecture

The system is built around **CrewAI** — an agent orchestration framework that enables role-based, goal-driven collaboration between LLM-powered agents.
<img width="2700" height="1568" alt="cwt_agent_architecture" src="https://github.com/user-attachments/assets/f945439e-aa7d-4fb1-9c61-7371717afa95" />




---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Required? |
|---|---|---|
| Python | 3.11+ | ✅ |
| Node.js | 20+ | ⚠️ Video rendering |
| FFmpeg | Latest | ⚠️ Audio processing |
| OpenRouter API Key | — | ✅ |
| Apify API Token | — | ⚠️ Optional (mock fallback) |
| ElevenLabs API Key | — | ⚠️ Optional (silent fallback) |

### Setup in 5 Steps

```bash
# 1. Clone the repo
git clone https://github.com/Vaibhav5012/Ads-Agent-Multi-Agent-AI-System-for-Automated-Ad-Creation
cd Ads-Agent-Multi-Agent-AI-System-for-Automated-Ad-Creation

# 2. Set up environment variables
cp .env.example .env
# Add your OPENROUTER_API_KEY to .env (minimum required)

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Remotion (optional — for video rendering)
cd remotion && npm install && cd ..

# 5. Run the pipeline
python main.py --mode pipeline --niche "trading"
```

> **No API keys?** The pipeline runs with mock data by default — great for local development and testing.

---

## 🖥️ Running Modes

### Mode 1 — Direct Pipeline
```bash
python main.py --mode pipeline --niche "trading"
```

### Mode 2 — FastAPI Server
```bash
python main.py --mode api --host 0.0.0.0 --port 8000
# Interactive docs → http://localhost:8000/docs
```

### Mode 3 — Docker
```bash
docker-compose up --build
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/generate-ad` | Trigger full pipeline for a niche |
| `POST` | `/api/v1/analyze-ads` | Analyse scraped ads from a file |
| `POST` | `/api/v1/create-video` | Create video from an existing script |
| `GET` | `/api/v1/status/{job_id}` | Check job status |
| `GET` | `/api/v1/jobs` | List all jobs |
| `GET` | `/api/v1/download/{job_id}` | Download final video |
| `POST` | `/api/v1/upload-company-data` | Upload brand context file |

**Example — Generate an Ad:**
```bash
curl -X POST http://localhost:8000/api/v1/generate-ad \
  -H "Content-Type: application/json" \
  -d '{"niche": "trading", "company_context": ""}'
```

---

## 📂 Output Structure

```
data/
├── scraped_ads/        # Raw competitor ad data (JSON)
├── analysis/           # Marketing insights from Analyst Agent
├── scripts/            # Scene-by-scene ad scripts (JSON)
└── videos/
    ├── audio/          # Per-scene audio files (MP3)
    ├── subtitles.json  # Subtitle data
    ├── subtitles.srt   # Subtitle file
    └── final_ad_*.mp4  # Final rendered video

logs/
└── cwt_*.log           # Pipeline execution logs
```

---

## 🔑 API Keys Setup

<details>
<summary><b>OpenRouter (Required)</b></summary>

1. Go to [openrouter.ai](https://openrouter.ai) and sign up
2. Navigate to **Keys → Create Key**
3. Add to `.env` as `OPENROUTER_API_KEY`
4. Free tier includes `meta-llama/llama-3.3-70b-instruct:free`

</details>

<details>
<summary><b>Apify (Optional — for live scraping)</b></summary>

1. Go to [apify.com](https://apify.com) and sign up
2. Navigate to **Settings → Integrations → API Tokens**
3. Add to `.env` as `APIFY_API_TOKEN`
4. Free tier includes $5/month in credits

</details>

<details>
<summary><b>ElevenLabs (Optional — for voiceover)</b></summary>

1. Go to [elevenlabs.io](https://elevenlabs.io) and sign up
2. Navigate to **Profile → API Keys**
3. Add to `.env` as `ELEVENLABS_API_KEY`
4. Free tier: 10,000 characters/month

</details>

<details>
<summary><b>Google Drive (Optional — for cloud output)</b></summary>

1. Create a project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable the **Google Drive API**
3. Create a **Service Account** and download the JSON key
4. Save as `credentials/service_account.json`
5. Set `GDRIVE_FOLDER_ID` in `.env`

</details>

---

## 🧩 Extending the Pipeline

Adding a new agent takes 3 steps:

**1. Create the agent** → `src/agents/new_agent.py`
```python
from crewai import Agent
from src.config.settings import get_settings

def create_my_agent() -> Agent:
    settings = get_settings()
    return Agent(
        role="My New Role",
        goal="What this agent achieves",
        backstory="Agent expertise and background",
        tools=[],
        llm=...,
        verbose=True,
    )
```

**2. Create the task** → `src/tasks/task_definitions.py`
```python
def create_my_task(agent: Agent) -> Task:
    return Task(
        description="Detailed task instructions...",
        expected_output="What the task should return",
        agent=agent,
    )
```

**3. Register in the crew** → `src/crew/ad_crew.py`
```python
my_agent = create_my_agent()
my_task = create_my_task(my_agent)
# Add to agents and tasks lists in build_crew()
```

---

## 🐛 Troubleshooting

| Error | Fix |
|---|---|
| `OPENROUTER_API_KEY is not set` | Copy `.env.example` → `.env` and add your key |
| `Apify scrape failed — using mock data` | Normal without an Apify token. Pipeline uses mock ads |
| `npx not found` / Remotion fails | Install Node.js 20+ and run `cd remotion && npm install` |
| `FFmpeg not found` | Install via `brew install ffmpeg` / `apt install ffmpeg` / `choco install ffmpeg` |
| `429 rate limit` | OpenRouter free tier has limits. Pipeline auto-retries with backoff |
| Import errors | Run from project root: `python main.py`, not from inside `src/` |

---

## 🛠️ Tech Stack

- **Agent Orchestration** — [CrewAI](https://crewai.com)
- **LLM Provider** — [OpenRouter](https://openrouter.ai) (Llama 3.3 70B)
- **Web Scraping** — [Apify](https://apify.com)
- **Text-to-Speech** — [ElevenLabs](https://elevenlabs.io)
- **Video Rendering** — [Remotion](https://remotion.dev)
- **API Framework** — [FastAPI](https://fastapi.tiangolo.com)
- **Containerization** — Docker

---

## 🤝 Contributing

Contributions are welcome! If you have ideas, fixes, or improvements:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-idea`
3. Commit your changes: `git commit -m "Add: your feature"`
4. Push and open a Pull Request

---

## 📄 License

MIT — free to use, modify, and build on.

---

<div align="center">
Built using CrewAI · OpenRouter · ElevenLabs · Remotion
</div>
