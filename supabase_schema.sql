-- ============================================
-- SUPABASE SCHEMA FOR EVALUATION CYCLE APP
-- ============================================
-- Run this SQL in your Supabase SQL Editor:
-- https://app.supabase.com/project/YOUR_PROJECT/sql
-- ============================================

-- 1. CREATE FEEDBACK TABLE
-- Stores all feedback from evaluators
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

-- 2. CREATE CALL SESSIONS TABLE
-- Stores call session data including transcripts
CREATE TABLE IF NOT EXISTS call_sessions (
    id SERIAL PRIMARY KEY,
    bot_name TEXT NOT NULL,
    session_id TEXT,
    transcript JSONB,
    duration_seconds INTEGER,
    like_dislike_feedback JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. CREATE INDEXES FOR FASTER QUERIES
CREATE INDEX IF NOT EXISTS idx_feedback_bot_name ON feedback(bot_name);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_session_id ON feedback(session_id);
CREATE INDEX IF NOT EXISTS idx_call_sessions_bot_name ON call_sessions(bot_name);
CREATE INDEX IF NOT EXISTS idx_call_sessions_created_at ON call_sessions(created_at DESC);

-- 4. ENABLE ROW LEVEL SECURITY (RLS)
-- This is optional but recommended for production
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_sessions ENABLE ROW LEVEL SECURITY;

-- 5. CREATE POLICIES (Allow all operations for now)
-- You can customize these policies based on your auth requirements
CREATE POLICY "Allow all feedback operations" ON feedback FOR ALL USING (true);
CREATE POLICY "Allow all call_sessions operations" ON call_sessions FOR ALL USING (true);

-- ============================================
-- OPTIONAL: USEFUL VIEWS
-- ============================================

-- View: Feedback summary by bot
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

-- View: Recent feedback
CREATE OR REPLACE VIEW recent_feedback AS
SELECT 
    id,
    bot_name,
    comment,
    rating,
    evaluator,
    created_at
FROM feedback
ORDER BY created_at DESC
LIMIT 50;

-- ============================================
-- SAMPLE QUERIES
-- ============================================

-- Get all feedback for a specific bot:
-- SELECT * FROM feedback WHERE bot_name = 'Bot 1' ORDER BY created_at DESC;

-- Get feedback statistics:
-- SELECT * FROM feedback_summary;

-- Get recent feedback:
-- SELECT * FROM recent_feedback;

-- Get average rating by bot:
-- SELECT bot_name, AVG(rating) as avg_rating FROM feedback GROUP BY bot_name;

