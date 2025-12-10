# Deployment Plan

This document outlines the step-by-step plan to deploy the Evaluation Cycle application to production.

---

## Overview

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────┐    ┌─────────────────┐                   │
│   │  Streamlit      │    │    Vercel       │                   │
│   │  Cloud          │◄───│    (Static)     │                   │
│   │                 │    │                 │                   │
│   │  • app.py       │    │  • vapi_call_   │                   │
│   │  • Main UI      │    │    widget.html  │                   │
│   │                 │    │  • vapi_        │                   │
│   │                 │    │    transcript   │                   │
│   └────────┬────────┘    └─────────────────┘                   │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐    ┌─────────────────┐                   │
│   │    Supabase     │    │      VAPI       │                   │
│   │    (Database)   │    │    (Voice AI)   │                   │
│   │                 │    │                 │                   │
│   │  ✅ Already     │    │  ✅ Already     │                   │
│   │     deployed    │    │     deployed    │                   │
│   └─────────────────┘    └─────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Services Used

| Service | Purpose | Cost |
|---------|---------|------|
| **Streamlit Cloud** | Host main application | Free |
| **Vercel** | Host VAPI HTML files | Free |
| **Supabase** | Database | Free (already set up) |
| **VAPI** | Voice AI | Pay-per-use |

**Total hosting cost: $0/month** (within free tiers)

---

## Current Status

### Already Done ✅

- [x] Supabase database created & configured
- [x] VAPI integration working locally
- [x] App working on localhost
- [x] Environment variables configured
- [x] All documentation created

### Pending ⏳

- [ ] Deploy static files to Vercel
- [ ] Update app.py for production
- [ ] Push to GitHub
- [ ] Deploy to Streamlit Cloud
- [ ] Configure production secrets

---

## Deployment Steps

### Step 1: Deploy VAPI HTML Files to Vercel

**Time:** 5 minutes

**Files to deploy:**
- `vapi_call_widget.html`
- `vapi_transcript.html`

**Instructions:**

1. Create a new folder for Vercel deployment:
   ```
   vapi-static/
   ├── vapi_call_widget.html
   ├── vapi_transcript.html
   └── vercel.json
   ```

2. Create `vercel.json` for CORS:
   ```json
   {
     "headers": [
       {
         "source": "/(.*)",
         "headers": [
           { "key": "Access-Control-Allow-Origin", "value": "*" }
         ]
       }
     ]
   }
   ```

3. Deploy to Vercel:
   ```bash
   cd vapi-static
   npx vercel --prod
   ```

4. Note your deployment URL (e.g., `https://vapi-static-xxx.vercel.app`)

---

### Step 2: Update app.py for Production

**Time:** 2 minutes

**Changes needed:**

1. Add environment variable for static URL:
   ```python
   VAPI_STATIC_URL = os.getenv('VAPI_STATIC_URL', 'http://localhost:8080')
   ```

2. Update iframe sources in `render_call_interface()`:
   ```python
   # Change from:
   src="http://localhost:8080/vapi_call_widget.html"
   
   # To:
   src=f"{VAPI_STATIC_URL}/vapi_call_widget.html"
   ```

3. Conditionally skip local HTTP server in cloud:
   ```python
   IS_CLOUD = os.getenv('STREAMLIT_CLOUD', 'false').lower() == 'true'
   
   if not IS_CLOUD:
       # Start local HTTP server
       ...
   ```

---

### Step 3: Push to GitHub

**Time:** 3 minutes

**Instructions:**

1. Create GitHub repository (if not exists)

2. Create `.gitignore`:
   ```
   .env
   __pycache__/
   *.pyc
   .streamlit/secrets.toml
   venv/
   ```

3. Push code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Evaluation Cycle app"
   git remote add origin https://github.com/YOUR_USERNAME/evaluation-cycle.git
   git push -u origin main
   ```

---

### Step 4: Deploy to Streamlit Cloud

**Time:** 5 minutes

**Instructions:**

1. Go to [share.streamlit.io](https://share.streamlit.io)

2. Click "New app"

3. Connect your GitHub repository

4. Configure:
   - **Repository:** your-username/evaluation-cycle
   - **Branch:** main
   - **Main file path:** app.py

5. Click "Deploy"

---

### Step 5: Configure Secrets in Streamlit Cloud

**Time:** 2 minutes

**Instructions:**

1. In Streamlit Cloud, go to your app → Settings → Secrets

2. Add secrets (TOML format):
   ```toml
   # VAPI Configuration
   VAPI_PUBLIC_KEY = "your_vapi_public_key"
   VAPI_ASSISTANT_ID = "your_assistant_id"
   
   # Supabase Configuration
   SUPABASE_URL = "https://tzejbgxkcurnkfxsgfjp.supabase.co"
   SUPABASE_KEY = "eyJ..."
   
   # Static files URL (from Vercel)
   VAPI_STATIC_URL = "https://your-project.vercel.app"
   
   # Cloud flag
   STREAMLIT_CLOUD = "true"
   ```

3. Click "Save"

4. Reboot the app

---

### Step 6: Test Everything

**Time:** 5 minutes

**Checklist:**

- [ ] App loads correctly
- [ ] Home page shows all bot cards
- [ ] Profile view works for The Traditionalist
- [ ] Voice call connects (The Traditionalist)
- [ ] Transcript displays during call
- [ ] Feedback saves to Supabase
- [ ] Check Supabase dashboard for saved data

---

## Timeline Summary

| Step | Task | Time |
|------|------|------|
| 1 | Deploy VAPI HTML to Vercel | 5 min |
| 2 | Update app.py | 2 min |
| 3 | Push to GitHub | 3 min |
| 4 | Deploy to Streamlit Cloud | 5 min |
| 5 | Configure secrets | 2 min |
| 6 | Test everything | 5 min |
| | **Total** | **~22 min** |

---

## URLs After Deployment

| Service | URL |
|---------|-----|
| **Main App** | `https://your-app.streamlit.app` |
| **Static Files** | `https://your-project.vercel.app` |
| **Database** | `https://supabase.com/dashboard/project/tzejbgxkcurnkfxsgfjp` |

---

## Troubleshooting

### App won't start

- Check Streamlit Cloud logs
- Verify all secrets are set correctly
- Ensure `requirements.txt` is complete

### Voice call not working

- Verify `VAPI_STATIC_URL` is set correctly
- Check browser console for errors
- Ensure Vercel deployment has CORS headers

### Database not saving

- Verify `SUPABASE_URL` and `SUPABASE_KEY` in secrets
- Check Supabase dashboard for errors
- Ensure tables exist (run schema if needed)

### Microphone permission denied

- HTTPS is required (Streamlit Cloud provides this)
- User must grant permission in browser
- Check that Vercel URL uses HTTPS

---

## Post-Deployment

### Monitoring

- **Streamlit Cloud:** View logs in dashboard
- **Supabase:** Check database usage in dashboard
- **VAPI:** Monitor usage in VAPI dashboard

### Updates

To update the deployed app:

1. Make changes locally
2. Commit and push to GitHub
3. Streamlit Cloud auto-deploys from main branch

```bash
git add .
git commit -m "Update: description of changes"
git push
```

---

## Quick Reference

### Local Development
```bash
streamlit run app.py
```

### Deploy Update
```bash
git add . && git commit -m "Update" && git push
```

### Check Logs
- Streamlit Cloud → App → Logs
- Supabase → Dashboard → Logs

---

## Ready to Deploy?

Follow the steps in order. Each step builds on the previous one.

**Estimated total time: 20-25 minutes**

