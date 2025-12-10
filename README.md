# Evaluation Cycle Platform

A Streamlit-based platform for evaluating AI voice agents with integrated VAPI voice calling and Supabase database storage.

---

## Features

- 🤖 **Multiple Bot Profiles**: Evaluate different AI personas (The Traditionalist, etc.)
- 📞 **Voice Call Mode**: Real-time voice calls with VAPI integration
- 📝 **Live Transcript**: See real-time transcription during voice calls
- 💬 **Feedback System**: Rate calls and provide written feedback
- 💾 **Database Storage**: All feedback saved to Supabase (PostgreSQL)
- 👤 **Profile View**: View detailed bot personality profiles
- 🎨 **Modern Dark UI**: Clean and intuitive interface

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
VAPI_ASSISTANT_ID=your_vapi_assistant_id

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

| Bot | Name | VAPI Enabled | Description |
|-----|------|--------------|-------------|
| Bot 1 | **The Traditionalist** | ✅ Yes | Physician who relies on established treatments |
| Bot 2 | Sales Excellence Coach | ❌ No | Coming soon |
| Bot 3 | Ibuprofen Knowledge Tester | ❌ No | Coming soon |
| Bot 4 | Breast Cancer Oncologist | ❌ No | Coming soon |
| Bot 5 | Herceptin Specialist | ❌ No | Coming soon |
| Bot 6 | Cardiology Expert | ❌ No | Coming soon |

---

## Project Structure

```
Evaluation_Cycle/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (create this)
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
VAPI_ASSISTANT_ID=your_assistant_id
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
```

### Production (Streamlit Cloud Secrets)

```toml
VAPI_PUBLIC_KEY = "your_public_key"
VAPI_ASSISTANT_ID = "your_assistant_id"
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
