# Database Setup Documentation

This document describes the Supabase database integration for the Evaluation Cycle application.

---

## Overview

**Database Provider:** Supabase (PostgreSQL)  
**Project ID:** `tzejbgxkcurnkfxsgfjp`  
**Region:** Default  
**Created:** December 2024

---

## What Was Done

### 1. Supabase Project Created

- Created a new Supabase project
- Obtained API credentials:
  - `SUPABASE_URL`: Project endpoint URL
  - `SUPABASE_KEY`: Anonymous/public API key for client-side access

### 2. Database Schema Created

Two tables were created to store evaluation data:

#### Table: `feedback`

Stores all feedback submitted by evaluators during bot evaluation sessions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Auto-incrementing primary key |
| `bot_name` | TEXT | Name of the bot being evaluated (e.g., "Bot 1") |
| `comment` | TEXT | Written feedback/comments from evaluator |
| `rating` | INTEGER | Rating from 1-5 stars |
| `evaluator` | TEXT | Name/ID of the person providing feedback |
| `session_id` | TEXT | Unique UUID for the browser session |
| `call_duration` | INTEGER | Duration of call in seconds |
| `transcript` | JSONB | Full conversation transcript as JSON |
| `created_at` | TIMESTAMPTZ | Timestamp when feedback was saved |

#### Table: `call_sessions`

Stores detailed call session data including full transcripts.

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Auto-incrementing primary key |
| `bot_name` | TEXT | Name of the bot |
| `session_id` | TEXT | Unique UUID for the browser session |
| `transcript` | JSONB | Full conversation transcript |
| `duration_seconds` | INTEGER | Call duration |
| `like_dislike_feedback` | JSONB | Per-message like/dislike data |
| `created_at` | TIMESTAMPTZ | Timestamp when session was saved |

### 3. Indexes Created

For faster query performance:

```sql
CREATE INDEX idx_feedback_bot_name ON feedback(bot_name);
CREATE INDEX idx_feedback_created_at ON feedback(created_at DESC);
CREATE INDEX idx_feedback_session_id ON feedback(session_id);
CREATE INDEX idx_call_sessions_bot_name ON call_sessions(bot_name);
CREATE INDEX idx_call_sessions_created_at ON call_sessions(created_at DESC);
```

### 4. Row Level Security (RLS)

RLS was enabled with permissive policies for initial development:

```sql
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all feedback operations" ON feedback FOR ALL USING (true);
CREATE POLICY "Allow all call_sessions operations" ON call_sessions FOR ALL USING (true);
```

> ⚠️ **Note:** For production, you should implement proper authentication and restrict these policies.

---

## Application Integration

### Files Modified

| File | Changes |
|------|---------|
| `requirements.txt` | Added `supabase>=2.0.0` |
| `.env` | Added `SUPABASE_URL` and `SUPABASE_KEY` |
| `app.py` | Added database helper functions |
| `supabase_schema.sql` | Created SQL schema file |

### Python Functions Added to `app.py`

```python
# Connection check
def is_db_connected() -> bool

# Save feedback
def save_feedback_to_db(bot_name, comment, rating, evaluator, call_duration, transcript) -> bool

# Save call session
def save_call_session_to_db(bot_name, transcript, duration, like_dislike_data) -> bool

# Retrieve feedback history
def get_feedback_history(bot_name, limit) -> list

# Get statistics
def get_feedback_stats() -> dict

# Session management
def get_session_id() -> str
```

### How Data Flows

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER ACTIONS                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STREAMLIT APP                              │
│                                                                 │
│  1. User makes a call with The Traditionalist                   │
│  2. User writes feedback in the feedback column                 │
│  3. User clicks "Save Feedback"                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    save_feedback_to_db()                        │
│                                                                 │
│  - Collects: bot_name, comment, rating, session_id              │
│  - Adds timestamp                                               │
│  - Sends to Supabase via API                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPABASE DATABASE                            │
│                                                                 │
│  PostgreSQL stores the data in the `feedback` table             │
│  Data is immediately available in Supabase dashboard            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Environment Variables

### Required in `.env`

```env
# Supabase Configuration
SUPABASE_URL=https://tzejbgxkcurnkfxsgfjp.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### For Streamlit Cloud Deployment

Add to Secrets in Streamlit Cloud dashboard:

```toml
SUPABASE_URL = "https://tzejbgxkcurnkfxsgfjp.supabase.co"
SUPABASE_KEY = "eyJ..."
```

---

## Viewing Data

### Option 1: Supabase Dashboard

1. Go to [https://supabase.com/dashboard/project/tzejbgxkcurnkfxsgfjp](https://supabase.com/dashboard/project/tzejbgxkcurnkfxsgfjp)
2. Click **Table Editor**
3. Select `feedback` or `call_sessions` table

### Option 2: SQL Queries

In Supabase SQL Editor:

```sql
-- View all feedback
SELECT * FROM feedback ORDER BY created_at DESC;

-- View feedback for specific bot
SELECT * FROM feedback WHERE bot_name = 'Bot 1';

-- Get average rating per bot
SELECT bot_name, AVG(rating) as avg_rating, COUNT(*) as total
FROM feedback
GROUP BY bot_name;

-- View recent call sessions
SELECT * FROM call_sessions ORDER BY created_at DESC LIMIT 10;
```

---

## Graceful Fallback

The application is designed to work **with or without** Supabase:

```python
if is_db_connected():
    save_feedback_to_db(...)
    st.success("✅ Feedback saved to database!")
else:
    st.success("✅ Feedback saved locally!")
```

If Supabase is not configured or unavailable:
- App continues to work normally
- Data is stored in Streamlit session state
- No errors are thrown

---

## Security Considerations

### Current State (Development)

- Using `anon` key (public, safe for client-side)
- RLS policies allow all operations
- No authentication required

### For Production

1. **Enable Authentication:**
   ```sql
   CREATE POLICY "Users can insert own feedback"
   ON feedback FOR INSERT
   WITH CHECK (auth.uid() IS NOT NULL);
   ```

2. **Use Service Role Key on Server:**
   - Keep `anon` key for client operations
   - Use `service_role` key for admin/backend operations

3. **Add Rate Limiting:**
   - Supabase has built-in rate limiting
   - Consider adding application-level limits

---

## Backup & Export

### Export Data via Dashboard

1. Go to Table Editor
2. Click on table
3. Click **Export** → **Download as CSV**

### Export via SQL

```sql
COPY feedback TO '/tmp/feedback_backup.csv' WITH CSV HEADER;
```

### Programmatic Backup

```python
# In Python
feedback = get_feedback_history(limit=10000)
import pandas as pd
df = pd.DataFrame(feedback)
df.to_csv('feedback_backup.csv', index=False)
```

---

## Troubleshooting

### "Failed to connect to Supabase"

- Check `SUPABASE_URL` format: must be `https://xxx.supabase.co`
- Check `SUPABASE_KEY`: must start with `eyJ`
- Verify project is active in Supabase dashboard

### "Failed to save feedback"

- Ensure tables exist (run `supabase_schema.sql`)
- Check RLS policies are created
- Look at Supabase logs for errors

### Data not appearing

- Refresh the Table Editor in Supabase
- Check the correct table (`feedback` vs `call_sessions`)
- Verify filters aren't hiding data

---

## Summary

| Item | Status |
|------|--------|
| Supabase project created | ✅ |
| Database tables created | ✅ |
| Indexes added | ✅ |
| RLS enabled | ✅ |
| Python SDK integrated | ✅ |
| Environment variables configured | ✅ |
| Graceful fallback implemented | ✅ |

The database is now ready to store all evaluation feedback and call session data!

