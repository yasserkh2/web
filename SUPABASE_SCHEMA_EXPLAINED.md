# Supabase Schema Explained

This document explains what each part of `supabase_schema.sql` does.

---

## File Overview

**File:** `supabase_schema.sql`  
**Purpose:** Set up the database structure to store evaluation data  
**Where to run:** Supabase SQL Editor

---

## Step-by-Step Breakdown

### Step 1: Create `feedback` Table (Lines 10-20)

```sql
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    bot_name TEXT NOT NULL,
    comment TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    evaluator TEXT,
    session_id TEXT,
    call_duration INTEGER,
    transcript JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**What this does:**
- Creates a table called `feedback`
- `IF NOT EXISTS` = Don't error if table already exists

**Columns explained:**

| Column | Type | Meaning |
|--------|------|---------|
| `id SERIAL PRIMARY KEY` | Auto-number | Unique ID (1, 2, 3...) automatically assigned |
| `bot_name TEXT NOT NULL` | Text (required) | Which bot was evaluated |
| `comment TEXT` | Text (optional) | Written feedback |
| `rating INTEGER CHECK (...)` | Number 1-5 | Star rating with validation |
| `evaluator TEXT` | Text (optional) | Who gave feedback |
| `session_id TEXT` | Text (optional) | Browser session identifier |
| `call_duration INTEGER` | Number (optional) | Call length in seconds |
| `transcript JSONB` | JSON data | Full conversation stored as JSON |
| `created_at TIMESTAMPTZ DEFAULT NOW()` | Timestamp | Auto-set to current time |

---

### Step 2: Create `call_sessions` Table (Lines 24-32)

```sql
CREATE TABLE IF NOT EXISTS call_sessions (
    id SERIAL PRIMARY KEY,
    bot_name TEXT NOT NULL,
    session_id TEXT,
    transcript JSONB,
    duration_seconds INTEGER,
    like_dislike_feedback JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**What this does:**
- Creates a table called `call_sessions`
- Stores detailed call data separately from feedback

**Columns explained:**

| Column | Type | Meaning |
|--------|------|---------|
| `id SERIAL PRIMARY KEY` | Auto-number | Unique ID |
| `bot_name TEXT NOT NULL` | Text (required) | Which bot was called |
| `session_id TEXT` | Text | Links to browser session |
| `transcript JSONB` | JSON data | Complete conversation |
| `duration_seconds INTEGER` | Number | How long the call lasted |
| `like_dislike_feedback JSONB` | JSON data | Per-message 👍/👎 ratings |
| `created_at TIMESTAMPTZ` | Timestamp | When session was saved |

---

### Step 3: Create Indexes (Lines 35-39)

```sql
CREATE INDEX IF NOT EXISTS idx_feedback_bot_name ON feedback(bot_name);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_session_id ON feedback(session_id);
CREATE INDEX IF NOT EXISTS idx_call_sessions_bot_name ON call_sessions(bot_name);
CREATE INDEX IF NOT EXISTS idx_call_sessions_created_at ON call_sessions(created_at DESC);
```

**What this does:**
- Creates "shortcuts" for the database to find data faster
- Like an index in a book - helps you find things quickly

**Why we need them:**

| Index | Speeds up queries like... |
|-------|---------------------------|
| `idx_feedback_bot_name` | "Get all feedback for Bot 1" |
| `idx_feedback_created_at` | "Get most recent feedback" |
| `idx_feedback_session_id` | "Get all feedback from this session" |
| `idx_call_sessions_bot_name` | "Get all calls for Bot 1" |
| `idx_call_sessions_created_at` | "Get most recent calls" |

**Without indexes:** Database scans ALL rows (slow)  
**With indexes:** Database jumps directly to matching rows (fast)

---

### Step 4: Enable Row Level Security (Lines 43-44)

```sql
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_sessions ENABLE ROW LEVEL SECURITY;
```

**What this does:**
- Turns ON the security system for each table
- By default, RLS blocks ALL access until you create policies

**Why we need it:**
- Controls who can see/edit data
- Important for production apps with multiple users

---

### Step 5: Create Policies (Lines 48-49)

```sql
CREATE POLICY "Allow all feedback operations" ON feedback FOR ALL USING (true);
CREATE POLICY "Allow all call_sessions operations" ON call_sessions FOR ALL USING (true);
```

**What this does:**
- Creates rules that say "allow everyone to do everything"
- `USING (true)` = Always allow

**Breaking it down:**

| Part | Meaning |
|------|---------|
| `CREATE POLICY` | Create a new access rule |
| `"Allow all feedback operations"` | Name of the rule |
| `ON feedback` | Apply to feedback table |
| `FOR ALL` | For SELECT, INSERT, UPDATE, DELETE |
| `USING (true)` | Always returns true = always allow |

**For production:** You would restrict this, for example:
```sql
-- Only allow users to see their own feedback
CREATE POLICY "Users see own feedback" ON feedback 
FOR SELECT USING (auth.uid() = user_id);
```

---

### Step 6: Create Views (Lines 56-79)

#### View 1: `feedback_summary`

```sql
CREATE OR REPLACE VIEW feedback_summary AS
SELECT 
    bot_name,
    COUNT(*) as total_feedback,
    AVG(rating) as avg_rating,
    COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_count,
    COUNT(CASE WHEN rating <= 2 THEN 1 END) as negative_count,
    MAX(created_at) as last_feedback_at
FROM feedback
GROUP BY bot_name
ORDER BY total_feedback DESC;
```

**What this does:**
- Creates a "saved query" called `feedback_summary`
- Automatically calculates statistics per bot

**Output example:**

| bot_name | total_feedback | avg_rating | positive_count | negative_count | last_feedback_at |
|----------|----------------|------------|----------------|----------------|------------------|
| Bot 1 | 25 | 4.2 | 20 | 2 | 2024-12-10 |
| Bot 2 | 10 | 3.5 | 5 | 3 | 2024-12-09 |

**How to use:**
```sql
SELECT * FROM feedback_summary;
```

#### View 2: `recent_feedback`

```sql
CREATE OR REPLACE VIEW recent_feedback AS
SELECT 
    id, bot_name, comment, rating, evaluator, created_at
FROM feedback
ORDER BY created_at DESC
LIMIT 50;
```

**What this does:**
- Shows the 50 most recent feedback entries
- Pre-sorted by newest first

**How to use:**
```sql
SELECT * FROM recent_feedback;
```

---

### Step 7: Sample Queries (Lines 85-95)

These are **comments** (not executed) - just examples for reference:

```sql
-- Get all feedback for a specific bot:
SELECT * FROM feedback WHERE bot_name = 'Bot 1' ORDER BY created_at DESC;

-- Get feedback statistics:
SELECT * FROM feedback_summary;

-- Get recent feedback:
SELECT * FROM recent_feedback;

-- Get average rating by bot:
SELECT bot_name, AVG(rating) as avg_rating FROM feedback GROUP BY bot_name;
```

---

## Summary: What Was Created

| Type | Name | Purpose |
|------|------|---------|
| **Table** | `feedback` | Store evaluator feedback |
| **Table** | `call_sessions` | Store call transcripts |
| **Index** | `idx_feedback_bot_name` | Fast bot filtering |
| **Index** | `idx_feedback_created_at` | Fast date sorting |
| **Index** | `idx_feedback_session_id` | Fast session lookup |
| **Index** | `idx_call_sessions_bot_name` | Fast bot filtering |
| **Index** | `idx_call_sessions_created_at` | Fast date sorting |
| **Policy** | "Allow all feedback operations" | Open access |
| **Policy** | "Allow all call_sessions operations" | Open access |
| **View** | `feedback_summary` | Auto-calculated stats |
| **View** | `recent_feedback` | Last 50 entries |

---

## Visual Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     SUPABASE DATABASE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐            │
│  │   feedback TABLE    │    │ call_sessions TABLE │            │
│  ├─────────────────────┤    ├─────────────────────┤            │
│  │ id                  │    │ id                  │            │
│  │ bot_name           │    │ bot_name           │            │
│  │ comment            │    │ session_id         │            │
│  │ rating             │    │ transcript         │            │
│  │ evaluator          │    │ duration_seconds   │            │
│  │ session_id         │    │ like_dislike_feedback│           │
│  │ call_duration      │    │ created_at         │            │
│  │ transcript         │    └─────────────────────┘            │
│  │ created_at         │                                       │
│  └─────────────────────┘                                       │
│           │                          │                         │
│           ▼                          ▼                         │
│  ┌─────────────────────────────────────────────────┐          │
│  │              INDEXES (5 total)                  │          │
│  │  Speed up: bot_name, created_at, session_id    │          │
│  └─────────────────────────────────────────────────┘          │
│                          │                                     │
│                          ▼                                     │
│  ┌─────────────────────────────────────────────────┐          │
│  │           ROW LEVEL SECURITY + POLICIES         │          │
│  │           (Currently: Allow all access)         │          │
│  └─────────────────────────────────────────────────┘          │
│                          │                                     │
│                          ▼                                     │
│  ┌─────────────────────────────────────────────────┐          │
│  │                    VIEWS                        │          │
│  │  • feedback_summary (stats per bot)            │          │
│  │  • recent_feedback (last 50 entries)           │          │
│  └─────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

**To see your tables:**
```sql
SELECT * FROM feedback;
SELECT * FROM call_sessions;
```

**To see statistics:**
```sql
SELECT * FROM feedback_summary;
```

**To see recent activity:**
```sql
SELECT * FROM recent_feedback;
```

