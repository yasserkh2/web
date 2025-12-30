# Evaluation Cycle Platform

A Streamlit-based platform for evaluating AI voice agents with integrated VAPI voice calling and Supabase database storage.

---

## Features

- 🤖 **6 Bot Profiles**: Evaluate different AI personas (customer segments)
- 📞 **Voice Call Mode**: Real-time voice calls with VAPI integration
- 📝 **Live Transcript**: See real-time transcription during voice calls
- 💬 **Feedback System**: Rate calls and provide written feedback
- 💾 **Database Storage**: All feedback saved to Supabase (PostgreSQL)
- 👤 **Profile View**: View detailed bot personality profiles
- 🎨 **Modern Dark UI**: Clean and intuitive interface
- 📊 **MLflow Prompt Registry**: Version control for prompts with compare & rollback
- 🔄 **Prompt Versioning**: Track every prompt change with commit messages

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

## Bots (Customer Segments)

| Name | Env Variable | Persona | Description |
|------|--------------|---------|-------------|
| **The Traditionalist** | `VAPI_ASSISTANT_ID_1` | Conservative | Relies on established, time-tested treatments |
| **The Innovator** | `VAPI_ASSISTANT_ID_2` | Early Adopter | Early adopter of new treatments, follows KOLs |
| **The Patient-Centered Physician** | `VAPI_ASSISTANT_ID_3` | QoL-Focused | Focuses on patient preferences and outcomes |
| **The Financially Driven** | `VAPI_ASSISTANT_ID_4` | Revenue-Focused | Practice profitability, reimbursement-aware |
| **The Evidence Purist** | `VAPI_ASSISTANT_ID_5` | Data-Driven | Strictly follows clinical evidence and RCT data |
| **The Cost-Conscious Prescriber** | `VAPI_ASSISTANT_ID_6` | Value-Aware | Balances efficacy with cost-effectiveness |

All bots support VAPI voice calls when their respective assistant ID is configured.
Prompts are stored in `prompts/*.md` and tracked in MLflow Prompt Registry.

---

## Project Structure

```
Evaluation_Cycle/
├── app.py                          # Main Streamlit application
├── mlflow_tracker.py               # Simple MLflow prompt/feedback tracker
├── prompts.py                      # Prompt engineering & MLflow integration
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (create this)
│
├── prompts/                        # Bot prompts (separate .md files)
│   ├── config.json                 # Bot metadata & evaluation criteria
│   ├── the_traditionalist.md       # Full prompt for The Traditionalist
│   ├── the_innovator.md            # Full prompt for The Innovator
│   ├── the_evidence_purist.md      # Full prompt for The Evidence Purist
│   ├── the_patient_centered.md     # Full prompt for Patient-Centered
│   ├── the_cost_conscious.md       # Full prompt for Cost-Conscious
│   └── the_financially_driven.md   # Full prompt for Financially Driven
│
├── evaluation/                     # Evaluation module
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py                     # CLI entry point
│   ├── config.py                   # Bot & MLflow configuration
│   ├── models.py                   # Data models
│   ├── evaluators/                 # Evaluation strategies
│   │   ├── base.py
│   │   ├── llm_evaluator.py        # GPT-based evaluator
│   │   └── manual_evaluator.py
│   └── services/                   # Business logic
│       ├── bot_service.py
│       ├── excel_service.py
│       ├── evaluation_service.py
│       └── mlflow_service.py       # MLflow tracking integration
│
├── mlruns/                         # MLflow tracking data (auto-created)
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

## MLflow Experiment Tracking

Track prompts, feedback, and evaluation metrics with MLflow.

### Quick Start

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Log feedback for a bot
python mlflow_tracker.py --log-feedback "The Innovator" "Should sound bolder about early adoption"

# Log an evaluation score
python mlflow_tracker.py --log-eval "The Innovator" 7.5

# View history
python mlflow_tracker.py --list

# Launch MLflow UI
python mlflow_tracker.py --ui
```

---

## Prompt Engineering

Manage and version prompts for each bot using **MLflow Prompt Registry**.

### Prompt Files

Prompts are stored as separate `.md` files in the `prompts/` folder:

```
prompts/
├── config.json                 # Bot metadata & evaluation criteria
├── the_traditionalist.md       # ~7,200 words
├── the_innovator.md            # ~7,500 words
├── the_evidence_purist.md      # ~5,900 words
├── the_patient_centered.md     # ~6,500 words
├── the_cost_conscious.md       # ~6,300 words
└── the_financially_driven.md   # ~6,400 words
```

### Quick Commands

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# List all bot prompts with word counts
python prompts.py --list

# Show full prompt for a bot
python prompts.py --show "The Innovator"

# Register prompt to MLflow Prompt Registry
python prompts.py --register "The Innovator"

# Register all prompts to MLflow
python prompts.py --register-all

# Evaluate prompt with GenAI (requires OPENAI_API_KEY)
python prompts.py --evaluate "The Innovator"

# Compare all prompts
python prompts.py --compare

# Start MLflow UI
python prompts.py --ui
```

### Editing Prompts

1. **Edit the `.md` file** directly in `prompts/` folder
2. **Register the new version** to MLflow:
   ```powershell
   python prompts.py --register "The Innovator"
   ```
3. **View version history** in MLflow UI: http://localhost:5000/#/prompts

### Bot Metadata

Edit `prompts/config.json` to update metadata:

```json
{
  "The Innovator": {
    "version": "1.0",
    "prompt_file": "the_innovator.md",
    "persona_notes": "Early adopter, conference-oriented, excited about novel MOA",
    "target_audience": "Pharma reps with new/innovative treatments",
    "evaluation_criteria": {
      "persona_alignment": "Shows genuine interest in innovation",
      "boldness": "Sounds confident about early adoption",
      "kol_references": "References conferences, KOLs, emerging research"
    }
  }
}
```

### Available Bots (Customer Segments)

| Bot | Persona | Key Traits |
|-----|---------|------------|
| **The Traditionalist** | Conservative | Prefers proven, time-tested treatments |
| **The Innovator** | Early Adopter | Excited about novel MOA, follows KOLs |
| **The Evidence Purist** | Data-Driven | Demands RCT data, questions methodology |
| **The Patient-Centered Physician** | QoL-Focused | Prioritizes patient preferences |
| **The Cost-Conscious Prescriber** | Value-Aware | Balances efficacy with cost |
| **The Financially Driven** | Revenue-Focused | Practice profitability, reimbursement |

### MLflow Prompt Registry

Access the Prompts dashboard at **http://localhost:5000/#/prompts**

**Features:**
- 📝 **Version Control**: Track every prompt change with commit messages
- 🔀 **Compare Versions**: Side-by-side diff between versions
- 🏷️ **Aliases**: Set "production", "staging" aliases for A/B testing
- 📊 **Metadata**: Track word count, persona, target audience
- 🚀 **Use in Code**: Copy prompt URI for use in applications

### Start MLflow UI

```powershell
# Using prompts.py
python prompts.py --ui

# Or directly
python -m mlflow ui --port 5000
```

### What Gets Tracked

| Type | Data Logged |
|------|-------------|
| **Prompts** | Full prompt text, version, word count, metadata tags |
| **Feedback** | Bot name, feedback text, category, suggestions |
| **Evaluations** | Bot name, score (0-10), LLM evaluation results |

### Environment Variables (Optional)

```env
MLFLOW_TRACKING_URI=mlruns              # Local folder (default)
OPENAI_API_KEY=sk-...                   # For GenAI evaluation
```

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
VAPI_PUBLIC_KEY=your_public_key
VAPI_ASSISTANT_ID_1=assistant_id_for_bot_1
VAPI_ASSISTANT_ID_2=assistant_id_for_bot_2
VAPI_ASSISTANT_ID_3=assistant_id_for_bot_3
VAPI_ASSISTANT_ID_4=assistant_id_for_bot_4
VAPI_ASSISTANT_ID_5=assistant_id_for_bot_5
VAPI_ASSISTANT_ID_6=assistant_id_for_bot_6
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
openpyxl>=3.1.0
mlflow>=2.9.0
openai>=1.0.0
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
