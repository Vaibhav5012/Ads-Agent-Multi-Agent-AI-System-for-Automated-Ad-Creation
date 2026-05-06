# CrowdWisdomTrading — AI-Powered Ads Creation Pipeline

> A production-grade backend system using **4 CrewAI agents** to automatically
> scrape, analyse, script, and produce 60-second video ads for trading/finance brands.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     FastAPI REST API (:8000)                     │
│  POST /generate-ad │ POST /analyze-ads │ POST /create-video     │
│  GET  /status/:id  │ GET  /jobs        │ GET  /download/:id     │
└──────────────┬───────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    CrewAI Sequential Pipeline                    │
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌──────┐│
│  │  Agent 1:   │──▶│  Agent 2:   │──▶│  Agent 3:   │──▶│Agent ││
│  │  Ad Search  │   │  Marketing  │   │  Script     │   │  4:  ││
│  │  Specialist │   │  Analyst    │   │  Writer     │   │Video ││
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └──┬───┘│
│         │                 │                 │              │    │
│    Apify SDK        LLM Analysis      GDrive + LLM   ElevenLabs│
│    (Meta Ads)                                         + Remotion│
└──────────────────────────────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Output Files                              │
│  data/scraped_ads/  │  data/analysis/  │  data/scripts/         │
│                     │                  │  data/videos/*.mp4     │
└──────────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

| Requirement | Version | Required? |
|---|---|---|
| Python | 3.11+ | ✅ Yes |
| Node.js | 20+ | ⚠️ For video rendering |
| FFmpeg | Latest | ⚠️ For audio processing |
| OpenRouter API Key | — | ✅ Yes |
| Apify API Token | — | ⚠️ Optional (mock fallback) |
| ElevenLabs API Key | — | ⚠️ Optional (silent fallback) |
| Google Drive credentials | — | ⚠️ Optional (local fallback) |

## 🚀 Quick Start in 5 Commands

```bash
# 1. Clone the repository
git clone <your-repo-url> cwt-ads-agent && cd cwt-ads-agent

# 2. Create and configure environment
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY (required)

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Remotion dependencies (optional, for video rendering)
cd remotion && npm install && cd ..

# 5. Run the pipeline
python main.py --mode pipeline --niche "trading"
```

## 🔑 API Keys — Where to Get Them

### OpenRouter (Required)
1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up / log in
3. Navigate to **Keys** → **Create Key**
4. Copy the key → set as `OPENROUTER_API_KEY` in `.env`
5. The free tier includes `meta-llama/llama-3.3-70b-instruct:free`

### Apify (Optional)
1. Go to [apify.com](https://apify.com)
2. Sign up for a free account
3. Go to **Settings** → **Integrations** → **API tokens**
4. Create a token → set as `APIFY_API_TOKEN` in `.env`
5. The free tier includes $5/month in platform credits

### ElevenLabs (Optional)
1. Go to [elevenlabs.io](https://elevenlabs.io)
2. Sign up for a free account
3. Go to **Profile** → **API Keys**
4. Copy the key → set as `ELEVENLABS_API_KEY` in `.env`
5. Free tier includes 10,000 characters/month

### Google Drive Service Account (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable the **Google Drive API**
3. Create a **Service Account** → Download the JSON key
4. Save it as `credentials/service_account.json`
5. Share the target Drive folder with the service account email
6. Set the folder ID as `GDRIVE_FOLDER_ID` in `.env`

## 🖥️ Running Modes

### Mode 1: Direct Pipeline Execution
```bash
python main.py --mode pipeline --niche "trading"
```

### Mode 2: FastAPI Server
```bash
python main.py --mode api --host 0.0.0.0 --port 8000
# Docs: http://localhost:8000/docs
```

### Mode 3: Docker
```bash
docker-compose up --build
```

## 📡 API Endpoints

### Generate a Full Ad
```bash
curl -X POST http://localhost:8000/api/v1/generate-ad \
  -H "Content-Type: application/json" \
  -d '{"niche": "trading", "company_context": ""}'
```

### Analyse Existing Ads
```bash
curl -X POST http://localhost:8000/api/v1/analyze-ads \
  -H "Content-Type: application/json" \
  -d '{"ads_file_path": "data/scraped_ads/ads_latest.json"}'
```

### Create Video from Script
```bash
curl -X POST http://localhost:8000/api/v1/create-video \
  -H "Content-Type: application/json" \
  -d '{"script_file_path": "data/scripts/script_latest.json"}'
```

### Check Job Status
```bash
curl http://localhost:8000/api/v1/status/{job_id}
```

### List All Jobs
```bash
curl http://localhost:8000/api/v1/jobs
```

### Download Final Video
```bash
curl -O http://localhost:8000/api/v1/download/{job_id}
```

### Upload Company Data
```bash
curl -X POST http://localhost:8000/api/v1/upload-company-data \
  -F "file=@my_company_info.md"
```

## 📂 Output File Locations

| Output | Location |
|---|---|
| Scraped ads | `data/scraped_ads/ads_*.json` |
| Marketing analysis | `data/analysis/analysis_*.json` |
| Ad scripts | `data/scripts/script_*.json` |
| Audio files | `data/videos/audio/scene_*.mp3` |
| Subtitles | `data/videos/subtitles.json`, `subtitles.srt` |
| Final video | `data/videos/final_ad_*.mp4` |
| Job database | `data/jobs.json` |
| Logs | `logs/cwt_*.log` |

## 🧩 How to Extend: Adding a New Agent

1. **Create the agent** in `src/agents/new_agent.py`:
   ```python
   from crewai import Agent
   from langchain_openai import ChatOpenAI
   from src.config.settings import get_settings

   def create_my_agent() -> Agent:
       settings = get_settings()
       llm = ChatOpenAI(
           model=settings.openrouter_model,
           openai_api_key=settings.openrouter_api_key,
           openai_api_base=settings.openrouter_base_url,
       )
       return Agent(
           role="My New Role",
           goal="What this agent achieves",
           backstory="Agent's expertise and background",
           tools=[],
           llm=llm,
           verbose=True,
       )
   ```

2. **Create the task** in `src/tasks/task_definitions.py`:
   ```python
   def create_my_task(agent: Agent) -> Task:
       return Task(
           description="Detailed task instructions...",
           expected_output="What the task should return",
           agent=agent,
       )
   ```

3. **Add to the crew** in `src/crew/ad_crew.py`:
   ```python
   # In build_crew():
   my_agent = create_my_agent()
   my_task = create_my_task(my_agent)
   # Add to agents and tasks lists
   ```

## 🐛 Troubleshooting

### "OPENROUTER_API_KEY is not set"
→ Create a `.env` file from `.env.example` and add your OpenRouter key.

### "Apify scrape failed — using mock data"
→ This is normal if `APIFY_API_TOKEN` is not set. The pipeline will use realistic mock ads for development.

### "npx not found" or Remotion render fails
→ Install Node.js 20+ and run `cd remotion && npm install`.

### "FFmpeg not found"
→ Install FFmpeg: `choco install ffmpeg` (Windows) / `brew install ffmpeg` (macOS) / `apt install ffmpeg` (Linux).

### LLM rate limiting (429 errors)
→ The free OpenRouter model has rate limits. The pipeline includes retry logic with exponential backoff. Wait a few minutes and retry.

### Import errors
→ Make sure you're running from the project root: `python main.py` (not from inside `src/`).

## 📄 License

MIT

---

Built with ❤️ using [CrewAI](https://crewai.com), [OpenRouter](https://openrouter.ai), [ElevenLabs](https://elevenlabs.io), and [Remotion](https://remotion.dev).
