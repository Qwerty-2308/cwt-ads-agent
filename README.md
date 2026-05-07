# CrowdWisdomTrading Daily Ads AI Agent

A 4-agent CrewAI pipeline that researches winning trading ads, extracts marketing insights, writes a 60-second ad script, and renders a complete MP4 video — fully automated.

## Architecture

```
┌─────────────────────┐    ┌──────────────────────┐
│   Agent 1           │    │   Agent 2            │
│   Ad Researcher     │───▶│ Marketing Analyzer   │
│   (Apify + Meta Ads)│    │   (LLM analysis)     │
└─────────────────────┘    └──────────┬───────────┘
                                      │
┌─────────────────────┐    ┌──────────▼───────────┐
│   Agent 4           │    │   Agent 3            │
│   Video Creator     │◀───│   Script Writer      │
│ (Images+Voice+Render│    │  (GDrive + LLM)      │
└─────────────────────┘    └──────────────────────┘
```

**Agent 1 — Ad Researcher**
- Scrapes Meta (Facebook/Instagram) Ads Library via Apify
- Targets trading/finance niche: signals, options, day trading
- Filters last 30 days, ranks by impressions
- Saves full results → `output/ads_research.json`

**Agent 2 — Marketing Analyzer**
- Reads winning ads and extracts pain points, hooks, frameworks
- Identifies top emotional triggers and CTAs that appear across multiple ads
- Produces structured brief → `output/marketing_analysis.json`

**Agent 3 — Script Writer**
- Fetches CWT product data from Google Drive (or local `data/product_data.md`)
- Combines pain points + product USPs into a 60-second AIDA script
- Includes narration text, subtitle segments, and image prompts
- Saves → `output/ad_script.json`

**Agent 4 — Video Creator**
- Generates 6 scene images via Pollinations.ai (free, no key required)
- Generates voice narration via ElevenLabs (gTTS fallback)
- Assembles and renders MP4 via Remotion with subtitles + branding
- Final output → `output/ad_video.mp4`

## Tech Stack

| Component | Tool |
|-----------|------|
| Agent framework | [CrewAI](https://docs.crewai.com/) |
| LLM provider | [OpenRouter](https://openrouter.ai/) — `nvidia/nemotron-3-super-120b:free` |
| Ad scraping | [Apify](https://apify.com/) — Meta Ads Library actor |
| Image generation | [Pollinations.ai](https://pollinations.ai/) — free, no key |
| Voice | [ElevenLabs](https://elevenlabs.io/) + gTTS fallback |
| Video rendering | [Remotion](https://www.remotion.dev/) |
| Language | Python 3.11+ |

## Setup

### 1. Clone and install Python deps

```bash
git clone https://github.com/YOUR_USERNAME/cwt-ads-agent
cd cwt-ads-agent
pip install -e .
```

### 2. Install Remotion (Node.js required)

```bash
cd video && npm install && cd ..
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

Required keys in `.env`:

```
OPENROUTER_API_KEY=sk-or-v1-...     # https://openrouter.ai
APIFY_API_TOKEN=apify_api_...       # https://apify.com
ELEVENLABS_API_KEY=sk_...           # https://elevenlabs.io (optional — gTTS used if missing)
```

Optional:
```
GDRIVE_FOLDER_ID=                   # Your GDrive folder with CWT product data
GOOGLE_SERVICE_ACCOUNT_JSON=service_account.json
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM   # Rachel (default)
```

### 4. Run the pipeline

```bash
# Full 4-agent pipeline
python main.py

# Or run video generation standalone (after main.py generates the script)
python generate_video.py
```

## Output Files

| File | Description |
|------|-------------|
| `output/ads_research.json` | Top performing Meta ads (last 30 days) |
| `output/marketing_analysis.json` | Extracted pain points and hooks |
| `output/ad_script.json` | 60-second script with segments and image prompts |
| `output/voice.mp3` | Generated voice narration |
| `output/images/` | AI-generated scene images |
| `output/ad_video.mp4` | Final rendered 60-second ad |

## Google Drive Integration

Agent 3 can read product data directly from your Google Drive:

1. Create a Google Cloud service account with Drive read access
2. Share your product data folder with the service account email
3. Set `GDRIVE_FOLDER_ID` and `GOOGLE_SERVICE_ACCOUNT_JSON` in `.env`

Without GDrive configured, Agent 3 uses `data/product_data.md` as product context.

## Apify Tokens

This project uses the Apify Meta Ads Library scraper:
- **Actor**: `apify/facebook-ads-library-scraper`
- **Token**: Set `APIFY_API_TOKEN` in `.env`
- Free tier includes enough credits for regular pipeline runs
- Results cached to `output/ads_research.json` to avoid re-scraping

## Scaling

For production use:
- **Parallel image generation**: Replace Pollinations with a paid API (Stability AI, DALL-E 3) and use `ThreadPoolExecutor` in `ImageGenTool`
- **Multiple niches**: Parameterise `CWT_SEARCH_TERMS` via CLI args to target different product verticals
- **Scheduled runs**: Wrap `main.py` in a cron job or Airflow DAG for daily ad refresh
- **Higher-quality voice**: Swap gTTS fallback for a fully-credentialed ElevenLabs key with TTS permissions

## Project Structure

```
cwt-ads-agent/
├── main.py                          # Entry point — runs full pipeline
├── generate_video.py                # Standalone video generator
├── pyproject.toml
├── .env.example
├── data/
│   └── product_data.md              # CWT product context (GDrive fallback)
├── src/
│   └── cwt_ads_agent/
│       ├── config.py                # All settings + paths
│       ├── crew.py                  # CrewAI crew definition
│       ├── main.py                  # Pipeline runner
│       ├── tools/
│       │   ├── apify_ads.py         # Meta Ads Library scraper
│       │   ├── gdrive_tool.py       # GDrive + local fallback
│       │   ├── image_gen.py         # Pollinations.ai image generator
│       │   ├── elevenlabs_voice.py  # Voice synthesis + gTTS fallback
│       │   └── remotion_render.py   # Video rendering
│       └── utils/
│           └── logger.py            # Structured logging
├── video/                           # Remotion composition (Node.js)
│   ├── src/
│   │   ├── index.ts
│   │   ├── Root.tsx
│   │   └── AdComposition.tsx        # Video layout with subtitles + branding
│   └── public/                      # Runtime assets (voice, images)
└── output/                          # Pipeline outputs (gitignored)
    ├── ads_research.json
    ├── marketing_analysis.json
    ├── ad_script.json
    ├── voice.mp3
    ├── images/
    └── ad_video.mp4
```
