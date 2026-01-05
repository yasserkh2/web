# Evaluation Cycle Platform

A Streamlit-based platform for evaluating AI voice agents with integrated VAPI voice calling and Supabase database storage.

---

## Features

- 🤖 **Multiple Bot Profiles**: Evaluate different AI personas (The Traditionalist, The Innovator, The Evidence Purist)
- 📞 **Voice Call Mode**: Real-time voice calls with VAPI integration
- 📝 **Live Transcript**: See real-time transcription during voice calls
- 💬 **Feedback System**: Rate calls and provide written feedback
- 💾 **Database Storage**: All feedback saved to Supabase (PostgreSQL)
- 👤 **Profile View**: View detailed bot personality profiles
- 🎨 **Modern Dark UI**: Clean and intuitive interface
- 🤖 **LLM-Based Evaluation**: Automated segment-fit evaluation using GPT-4o-mini
- 📊 **Excel Integration**: Direct read/write to Excel evaluation sheets

---

## Quick Start

### 1. Setup Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# VAPI Configuration
VAPI_PUBLIC_KEY=your_vapi_public_key

# VAPI Assistant IDs (one for each bot)
VAPI_ASSISTANT_ID_1=your_assistant_id_for_bot_1  # The Traditionalist
VAPI_ASSISTANT_ID_2=your_assistant_id_for_bot_2  # The Innovator
VAPI_ASSISTANT_ID_3=your_assistant_id_for_bot_3  # The Patient-Centered Physician
VAPI_ASSISTANT_ID_4=your_assistant_id_for_bot_4  # The Financially Driven Prescriber
VAPI_ASSISTANT_ID_5=your_assistant_id_for_bot_5  # The Evidence Purist
VAPI_ASSISTANT_ID_6=your_assistant_id_for_bot_6  # The Cost-Conscious Prescriber

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Setup Database

Run `supabase_schema.sql` in your Supabase SQL Editor to create tables.

### 4. Run the App

```bash
streamlit run app.py
```

The app will:
- Start on `http://localhost:8501`
- Auto-start an HTTP server on port 8080 for voice calls
- Connect to Supabase for data storage

---

## Bots

| Name | Env Variable | Description |
|------|--------------|-------------|
| **The Traditionalist** | `VAPI_ASSISTANT_ID_1` | Relies on established, time-tested treatments |
| **The Innovator** | `VAPI_ASSISTANT_ID_2` | Early adopter of new treatments and technologies |
| **The Patient-Centered Physician** | `VAPI_ASSISTANT_ID_3` | Focuses on patient preferences and outcomes |
| **The Financially Driven Prescriber** | `VAPI_ASSISTANT_ID_4` | Institution-focused, considers financial factors |
| **The Evidence Purist** | `VAPI_ASSISTANT_ID_5` | Strictly follows clinical evidence and data |
| **The Cost-Conscious Prescriber** | `VAPI_ASSISTANT_ID_6` | Balances efficacy with cost-effectiveness |

All bots support VAPI voice calls when their respective assistant ID is configured.

---

## Project Structure

```
Evaluation_Cycle/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (create this)
│
├── bot_evaluation_with_comments.xlsx  # Evaluation Excel file
│
├── src/                            # Source package (OOP/SOLID)
│   ├── __init__.py
│   ├── config.py                   # Configuration (paths, API keys, columns)
│   ├── models.py                   # Data classes (Segment, Response, Evaluation)
│   └── services/                   # Business logic services
│       ├── __init__.py
│       ├── segment_service.py      # Load segment personas from MD files
│       ├── excel_service.py        # Excel read/write operations
│       ├── evaluation_service.py   # LLM evaluation logic
│       └── vapi_service.py         # VAPI API integration
│
├── scripts/                        # CLI scripts
│   ├── get_responses.py            # 1. Get/manage VAPI responses
│   └── evaluate_responses.py       # 2. Evaluate responses with LLM
│
├── segments/                       # Segment persona descriptions
│   ├── the_traditionalist.md
│   ├── the_innovator.md
│   ├── the_evidence_purist.md
│   ├── the_cost_conscious.md
│   ├── the_financially_driven.md
│   └── the_patient_centered.md
│
├── vapi_call_widget.html           # Voice call interface
├── vapi_transcript.html            # Live transcript display
├── vapi_call.html                  # Full voice call page
│
├── supabase_schema.sql             # Database schema
│
├── .streamlit/
│   └── config.toml                 # Streamlit theme configuration
│
└── Documentation/
    ├── README.md                   # This file
    ├── DEPLOYMENT_PLAN.md          # Step-by-step deployment guide
    ├── DEPLOYMENT.md               # Deployment options & details
    ├── DATABASE_SETUP.md           # Database integration docs
    ├── DATABASE_OPTIONS.md         # Database comparison
    ├── SUPABASE_SCHEMA_EXPLAINED.md # SQL schema breakdown
    └── VAPI_INTEGRATION_GUIDE.md   # VAPI setup & troubleshooting
```

---

## Architecture (SOLID Principles)

### Single Responsibility
- `SegmentService` - Only loads segment data from MD files
- `ExcelService` - Only handles Excel read/write
- `EvaluationService` - Only handles LLM evaluation
- `VAPIService` - Only handles VAPI API calls

### Open/Closed
- Add new segments by creating new MD files (no code changes)
- Add new evaluators by extending `EvaluationService`

### Dependency Inversion
- Services depend on config abstractions, not hardcoded values
- `EvaluationService` depends on `SegmentService` interface

### Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                      PIPELINE                               │
├─────────────────────────────────────────────────────────────┤
│  Step 1: VALIDATE      Step 2: EVALUATE     Step 3: SAVE   │
│  ┌──────────────┐      ┌──────────────┐     ┌───────────┐  │
│  │ Check Excel  │  ──► │  LLM Score   │ ──► │   Excel   │  │
│  │ for responses│      │  + Comment   │     │   Update  │  │
│  └──────────────┘      └──────────────┘     └───────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Running the Pipeline

```powershell
# Full pipeline
python scripts/pipeline.py --model gpt-4o-mini --delay 30

# Dry run (preview)
python scripts/pipeline.py --dry-run

# Force re-evaluate
python scripts/pipeline.py --force

# Single segment
python scripts/pipeline.py --segment "The Innovator"
```

---

## LLM Evaluation System

### Overview

The platform includes an automated evaluation system that uses GPT-4o-mini to assess how well bot responses match their target physician segment.

### Running Scripts

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# 1. Check response status
python scripts/get_responses.py --status

# 2. Export missing responses
python scripts/get_responses.py --export missing.txt

# 3. Run LLM evaluation
python scripts/evaluate_responses.py --model gpt-4o-mini --delay 30

# 4. Force re-evaluate already scored rows
python scripts/evaluate_responses.py --force

# 5. Evaluate only one segment
python scripts/evaluate_responses.py --segment "The Innovator"

# 6. Dry run (see what would happen)
python scripts/evaluate_responses.py --dry-run
```

### Excel Structure

The evaluation uses `bot_evaluation_with_comments.xlsx` with the following structure:

| Column | Header | Description |
|--------|--------|-------------|
| A | Question | The question asked to the bot |
| **The Traditionalist** |||
| B | The Traditionalist | Bot's response |
| C | The Traditionalist Eval | LLM score (0-5) |
| D | The Traditionalist Comment | LLM comment (if score ≤ 3) |
| E | The Traditionalist Eval_Aboubakr | Human evaluator score |
| F | The Traditionalist Comment_Aboubakr | Human evaluator comment |
| G | The Traditionalist Eval_Thomas | Human evaluator score |
| H | The Traditionalist Comment_Thomas | Human evaluator comment |
| **The Innovator** |||
| I | The Innovator | Bot's response |
| J | The Innovator Eval | LLM score (0-5) |
| K | The Innovator Comment | LLM comment (if score ≤ 3) |
| L | The Innovator Eval_Aboubakr | Human evaluator score |
| M | The Innovator Comment_Aboubakr | Human evaluator comment |
| N | The Innovator Eval_Thomas | Human evaluator score |
| O | The Innovator Comment_Thomas | Human evaluator comment |
| **The Evidence Purist** |||
| P | The Evidence Purist | Bot's response |
| Q | The Evidence Purist Eval | LLM score (0-5) |
| R | The Evidence Purist Comment | LLM comment (if score ≤ 3) |
| S | The Evidence Purist Eval_Aboubakr | Human evaluator score |
| T | The Evidence Purist Comment_Aboubakr | Human evaluator comment |
| U | The Evidence Purist Eval_Thomas | Human evaluator score |
| V | The Evidence Purist Comment_Thomas | Human evaluator comment |

### Scoring Scale (0-5)

| Score | Meaning |
|-------|---------|
| 0 | Not the segment at all |
| 1 | Mostly wrong, few weak hints |
| 2 | Mixed, clear drift into other segments |
| 3 | Acceptable but inconsistent / noticeable leaks |
| 4 | Strong match with minor issues |
| 5 | Perfect, no leaks |

### Segment Descriptions

Segment profiles are stored in the `segments/` folder:
- `segments/the_traditionalist.md`
- `segments/the_innovator.md`
- `segments/the_evidence_purist.md`

These files contain detailed persona descriptions used by the LLM evaluator.

### Evaluation Prompt

The evaluator uses a strict segment-fit prompt that:
1. Loads the segment description from `segments/` folder
2. Compares the bot response against segment traits
3. Returns a score (0-5) and comment
4. Only adds comments when score ≤ 3 (needs improvement)

---

## Voice Call Feature

### How It Works

1. Click **📞 Call** on The Traditionalist card
2. The 3-column interface loads: Feedback | Call | Transcript
3. Click the **green call button** to start
4. **Allow microphone access** when prompted
5. Start speaking - the AI responds in real-time
6. View the **live transcript** on the right
7. Write feedback in the left column
8. Click **Save Feedback** to store in database

### Technical Details

- Voice calls use VAPI's WebRTC-based real-time communication
- Separate HTML files for call widget and transcript
- HTTP server on port 8080 serves voice pages
- localStorage enables cross-iframe communication
- Supabase stores all feedback and transcripts

---

## Database

### Tables

| Table | Purpose |
|-------|---------|
| `feedback` | Stores evaluator feedback, ratings, comments |
| `call_sessions` | Stores call transcripts and duration |

### Views

| View | Purpose |
|------|---------|
| `feedback_summary` | Statistics per bot |
| `recent_feedback` | Last 50 feedback entries |

See `SUPABASE_SCHEMA_EXPLAINED.md` for full details.

---

## Deployment

### Architecture

```
Streamlit Cloud ──► Vercel (Static HTML) ──► VAPI (Voice AI)
       │
       ▼
   Supabase (Database)
```

### Quick Deploy

1. Deploy HTML files to Vercel
2. Deploy app to Streamlit Cloud
3. Configure secrets

**Cost: $0/month** (all free tiers)

See `DEPLOYMENT_PLAN.md` for detailed steps.

---

## Environment Variables

### Local Development (`.env`)

```env
# OpenAI API Key (for LLM evaluation)
OPENAI_API_KEY=sk-...

# VAPI Configuration
VAPI_PUBLIC_KEY=your_public_key
VAPI_ASSISTANT_ID_1=assistant_id_for_bot_1
VAPI_ASSISTANT_ID_2=assistant_id_for_bot_2
VAPI_ASSISTANT_ID_3=assistant_id_for_bot_3
VAPI_ASSISTANT_ID_4=assistant_id_for_bot_4
VAPI_ASSISTANT_ID_5=assistant_id_for_bot_5
VAPI_ASSISTANT_ID_6=assistant_id_for_bot_6

# Supabase Configuration
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
```

### Production (Streamlit Cloud Secrets)

```toml
VAPI_PUBLIC_KEY = "your_public_key"
VAPI_ASSISTANT_ID_1 = "assistant_id_for_bot_1"
VAPI_ASSISTANT_ID_2 = "assistant_id_for_bot_2"
VAPI_ASSISTANT_ID_3 = "assistant_id_for_bot_3"
VAPI_ASSISTANT_ID_4 = "assistant_id_for_bot_4"
VAPI_ASSISTANT_ID_5 = "assistant_id_for_bot_5"
VAPI_ASSISTANT_ID_6 = "assistant_id_for_bot_6"
SUPABASE_URL = "https://xxx.supabase.co"
SUPABASE_KEY = "eyJ..."
VAPI_STATIC_URL = "https://your-project.vercel.app"
STREAMLIT_CLOUD = "true"
```

---

## Dependencies

```
streamlit>=1.28.0
requests>=2.31.0
python-dotenv>=1.0.0
supabase>=2.0.0
openai>=1.0.0
openpyxl>=3.1.0
mlflow>=2.0.0
```

---

## MLflow - Prompt Tracking

### Overview

We use MLflow to track evaluation prompts before making changes. This allows us to:
- Version control prompts
- Compare prompt performance
- Roll back to previous versions

### Start MLflow UI

```powershell
cd F:\CTC_HEALTH\Projects\Evaluation_Cycle
.\venv\Scripts\Activate.ps1
mlflow ui --port 5000
```

Open **http://localhost:5000** to view experiments.

### Track Current Prompt

Before changing the evaluation prompt, save it to MLflow:

```powershell
python scripts/track_prompt.py --name "prompt_v1" --description "Initial evaluation prompt"
```

### List Tracked Prompts

```powershell
python scripts/track_prompt.py --list
```

### Experiments

| Experiment | Description |
|------------|-------------|
| `customer_segments` | Segment persona models |
| `evaluation_prompts` | Evaluation prompt versions |

### Workflow

```
1. Track current prompt    →  python scripts/track_prompt.py
2. Make changes to prompt  →  Edit evaluation_service.py
3. Run pipeline            →  python scripts/pipeline.py
4. Compare results         →  MLflow UI (http://localhost:5000)
```

---

## Troubleshooting

### Voice Call Not Working

1. **Microphone permissions**: Click 🔒 in browser → Allow Microphone
2. **Check VAPI credentials**: Verify `.env` has correct keys
3. **Port 8080 in use**: Kill existing process:
   ```powershell
   netstat -ano | findstr :8080
   taskkill /PID <PID> /F
   ```

### Database Not Saving

1. Check `SUPABASE_URL` and `SUPABASE_KEY`
2. Ensure tables exist (run `supabase_schema.sql`)
3. Check Supabase dashboard for errors

### No Audio

1. Check system microphone settings
2. Verify VAPI Assistant has voice provider
3. Check VAPI dashboard for call logs

### LLM Evaluation Errors

1. **Rate limit errors**: Add payment method at https://platform.openai.com/account/billing
2. **Permission denied on Excel**: Close the Excel file before running
3. **API key not found**: Set `OPENAI_API_KEY` in `.env` or environment
4. **All scores 0**: Check for rate limit in the comment column

---

## Documentation

| Document | Purpose |
|----------|---------|
| `DEPLOYMENT_PLAN.md` | Step-by-step deployment guide |
| `DEPLOYMENT.md` | Deployment options & architecture |
| `DATABASE_SETUP.md` | Database integration details |
| `DATABASE_OPTIONS.md` | Why we chose Supabase |
| `SUPABASE_SCHEMA_EXPLAINED.md` | SQL schema breakdown |
| `VAPI_INTEGRATION_GUIDE.md` | VAPI setup & troubleshooting |

---

## License

MIT License
