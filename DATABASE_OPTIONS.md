# Database Options for Feedback Storage

This document outlines database options for storing feedback data in the Evaluation Cycle application, optimized for deployment with Streamlit Cloud.

---

## Table of Contents

1. [Requirements](#requirements)
2. [Options Comparison](#options-comparison)
3. [Recommended: Supabase](#recommended-supabase)
4. [Alternative: Google Sheets](#alternative-google-sheets)
5. [Other Options](#other-options)
6. [Implementation Guide](#implementation-guide)

---

## Requirements

For the feedback feature, we need to store:

| Field | Type | Description |
|-------|------|-------------|
| `id` | Auto-increment | Unique identifier |
| `bot_name` | Text | Name of the bot being evaluated |
| `comment` | Text | Feedback text |
| `rating` | Integer | Optional rating (1-5) |
| `evaluator` | Text | Who provided the feedback |
| `session_id` | Text | Unique session identifier |
| `created_at` | Timestamp | When feedback was submitted |

**Estimated Storage:** ~1KB per feedback entry → 500MB = ~500,000 entries

---

## Options Comparison

| Database | Setup Time | Free Tier | Speed | Streamlit Compatible | Best For |
|----------|------------|-----------|-------|---------------------|----------|
| **Supabase** ⭐ | 5 min | 500MB, 2 projects | Fast | ✅ Excellent | Production apps |
| **Google Sheets** | 10 min | Unlimited | Slow | ✅ Good | Quick prototypes |
| **Firebase Firestore** | 10 min | 1GB storage | Fast | ✅ Good | Real-time apps |
| **MongoDB Atlas** | 15 min | 512MB | Fast | ✅ Good | Document data |
| **Turso (SQLite)** | 5 min | 9GB, 500 DBs | Fast | ✅ Good | Edge computing |
| **Airtable** | 5 min | 1,200 records | Medium | ✅ Good | Non-technical teams |
| **Notion** | 10 min | Unlimited | Slow | ⚠️ Limited | Documentation |

---

## Recommended: Supabase

### Why Supabase?

```
✅ Free PostgreSQL database (500MB)
✅ Simple Python SDK (supabase-py)
✅ Works perfectly with Streamlit Cloud
✅ Web dashboard to view/edit data
✅ Built-in authentication (for future use)
✅ Real-time subscriptions available
✅ Row-level security for production
✅ Automatic API generation
```

### Setup Steps

#### 1. Create Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Sign up with GitHub
3. Create a new project
4. Wait for database to provision (~2 minutes)

#### 2. Create Feedback Table

Go to **SQL Editor** and run:

```sql
-- Create feedback table
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    bot_name TEXT NOT NULL,
    comment TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    evaluator TEXT,
    session_id TEXT,
    call_duration INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX idx_feedback_bot_name ON feedback(bot_name);
CREATE INDEX idx_feedback_created_at ON feedback(created_at DESC);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Allow all operations for now (customize later)
CREATE POLICY "Allow all operations" ON feedback FOR ALL USING (true);
```

#### 3. Get API Keys

1. Go to **Settings** → **API**
2. Copy:
   - `Project URL` (e.g., `https://xxxxx.supabase.co`)
   - `anon/public` key (safe for client-side)

#### 4. Install Python SDK

```bash
pip install supabase
```

Add to `requirements.txt`:
```
supabase
```

#### 5. Python Integration Code

```python
import os
from supabase import create_client, Client
from datetime import datetime

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_feedback(bot_name: str, comment: str, rating: int = None, 
                  evaluator: str = None, session_id: str = None):
    """Save feedback to Supabase"""
    data = {
        "bot_name": bot_name,
        "comment": comment,
        "rating": rating,
        "evaluator": evaluator,
        "session_id": session_id
    }
    
    result = supabase.table("feedback").insert(data).execute()
    return result.data

def get_feedback(bot_name: str = None, limit: int = 100):
    """Retrieve feedback from Supabase"""
    query = supabase.table("feedback").select("*")
    
    if bot_name:
        query = query.eq("bot_name", bot_name)
    
    result = query.order("created_at", desc=True).limit(limit).execute()
    return result.data

def get_feedback_stats():
    """Get feedback statistics"""
    result = supabase.table("feedback").select("bot_name, rating").execute()
    
    stats = {}
    for row in result.data:
        bot = row["bot_name"]
        if bot not in stats:
            stats[bot] = {"count": 0, "ratings": []}
        stats[bot]["count"] += 1
        if row["rating"]:
            stats[bot]["ratings"].append(row["rating"])
    
    # Calculate averages
    for bot in stats:
        ratings = stats[bot]["ratings"]
        stats[bot]["avg_rating"] = sum(ratings) / len(ratings) if ratings else None
    
    return stats
```

#### 6. Environment Variables

**Local (`.env`):**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

**Streamlit Cloud (Secrets):**
```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

### Supabase Dashboard

Access your data anytime at:
```
https://app.supabase.com/project/YOUR_PROJECT/editor
```

---

## Alternative: Google Sheets

### Why Google Sheets?

```
✅ Zero database knowledge required
✅ Anyone can view/edit the spreadsheet
✅ Easy export to Excel/CSV
✅ Free forever (with Google account)
✅ Familiar interface for non-technical users
```

### Limitations

```
⚠️ Slower than traditional databases
⚠️ 100 requests per 100 seconds limit
⚠️ Max 10 million cells per spreadsheet
⚠️ Less suitable for high-traffic apps
```

### Setup Steps

#### 1. Create Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create new project
3. Enable **Google Sheets API** and **Google Drive API**

#### 2. Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Create **Service Account**
3. Download JSON key file
4. Copy the `client_email` from the JSON

#### 3. Create Spreadsheet

1. Create new Google Sheet
2. Name it "Evaluation Feedback"
3. Add headers in Row 1:
   ```
   ID | Bot Name | Comment | Rating | Evaluator | Session ID | Created At
   ```
4. Share the sheet with the `client_email` (give Editor access)

#### 4. Install Libraries

```bash
pip install gspread google-auth
```

Add to `requirements.txt`:
```
gspread
google-auth
```

#### 5. Python Integration Code

```python
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import os

# Define scope
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_sheets_client():
    """Initialize Google Sheets client"""
    # For Streamlit Cloud, use secrets
    if os.getenv("GOOGLE_CREDENTIALS"):
        creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        # For local development, use JSON file
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    
    return gspread.authorize(creds)

def save_feedback_sheets(bot_name: str, comment: str, rating: int = None,
                         evaluator: str = None, session_id: str = None):
    """Save feedback to Google Sheets"""
    client = get_sheets_client()
    sheet = client.open("Evaluation Feedback").sheet1
    
    # Get next ID
    all_values = sheet.get_all_values()
    next_id = len(all_values)  # Row count = next ID (since row 1 is header)
    
    # Append row
    row = [
        next_id,
        bot_name,
        comment,
        rating or "",
        evaluator or "",
        session_id or "",
        datetime.now().isoformat()
    ]
    
    sheet.append_row(row)
    return {"id": next_id}

def get_feedback_sheets(bot_name: str = None):
    """Retrieve feedback from Google Sheets"""
    client = get_sheets_client()
    sheet = client.open("Evaluation Feedback").sheet1
    
    records = sheet.get_all_records()
    
    if bot_name:
        records = [r for r in records if r["Bot Name"] == bot_name]
    
    return records
```

#### 6. Environment Variables

**Local:** Place `credentials.json` in project root

**Streamlit Cloud (Secrets):**
```toml
GOOGLE_CREDENTIALS = '{"type": "service_account", "project_id": "...", ...}'
SPREADSHEET_ID = "your-spreadsheet-id"
```

---

## Other Options

### Firebase Firestore

```python
# pip install firebase-admin

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def save_feedback_firebase(bot_name, comment, rating=None):
    doc_ref = db.collection("feedback").document()
    doc_ref.set({
        "bot_name": bot_name,
        "comment": comment,
        "rating": rating,
        "created_at": firestore.SERVER_TIMESTAMP
    })
```

### MongoDB Atlas

```python
# pip install pymongo

from pymongo import MongoClient

client = MongoClient(os.getenv("MONGODB_URI"))
db = client.evaluation_cycle

def save_feedback_mongo(bot_name, comment, rating=None):
    db.feedback.insert_one({
        "bot_name": bot_name,
        "comment": comment,
        "rating": rating,
        "created_at": datetime.now()
    })
```

### Turso (SQLite Edge)

```python
# pip install libsql-experimental

import libsql_experimental as libsql

conn = libsql.connect("your-db.turso.io", auth_token=os.getenv("TURSO_TOKEN"))

def save_feedback_turso(bot_name, comment, rating=None):
    conn.execute(
        "INSERT INTO feedback (bot_name, comment, rating) VALUES (?, ?, ?)",
        (bot_name, comment, rating)
    )
    conn.commit()
```

---

## Implementation Guide

### Quick Decision Tree

```
                    ┌─────────────────────┐
                    │ Do you need SQL?    │
                    └─────────┬───────────┘
                              │
              ┌───────────────┴───────────────┐
              │ YES                           │ NO
              ▼                               ▼
    ┌─────────────────┐             ┌─────────────────┐
    │ Need real-time? │             │ Simple storage? │
    └────────┬────────┘             └────────┬────────┘
             │                                │
    ┌────────┴────────┐             ┌────────┴────────┐
    │ YES       │ NO  │             │ YES       │ NO  │
    ▼           ▼     │             ▼           ▼     │
 Supabase   Supabase  │         Sheets     Firestore  │
 (real-time)          │                               │
                      └───────────────────────────────┘
```

### Recommended Stack for This Project

```
┌────────────────────────────────────────────┐
│              RECOMMENDED STACK             │
├────────────────────────────────────────────┤
│  Frontend:     Streamlit Cloud (free)      │
│  Static Files: Vercel (free)               │
│  Database:     Supabase (free)             │
│  Voice AI:     VAPI (pay-as-you-go)        │
└────────────────────────────────────────────┘

Total Monthly Cost: $0 (within free tiers)
```

---

## Summary

| If you want... | Choose |
|----------------|--------|
| Best overall solution | **Supabase** |
| Simplest setup | **Google Sheets** |
| Real-time updates | **Supabase** or **Firebase** |
| Document storage | **MongoDB Atlas** |
| Edge performance | **Turso** |
| Non-technical team access | **Google Sheets** or **Airtable** |

---

## Next Steps

1. Choose your database (Supabase recommended)
2. Follow the setup steps above
3. Add environment variables
4. Update `app.py` to use the database functions
5. Test locally
6. Deploy to Streamlit Cloud

Need help implementing? Just ask!

