# Vercel Deployment Guide

This guide explains how to deploy the VAPI static files to Vercel for the voice call functionality.

---

## Why Vercel?

The voice call widget needs to be hosted on a separate static server because:

1. **Microphone Access** - Streamlit's sandboxed iframes block microphone permissions
2. **HTTPS Required** - Browsers require HTTPS for microphone access in production
3. **Same-Origin for localStorage** - Call widget and transcript need same origin (solved with combined widget)

---

## Files to Deploy

The `vapi-static/` folder contains:

```
vapi-static/
├── vapi_combined_widget.html   ← Main widget (call + transcript)
├── vapi_call_widget.html       ← Legacy (kept for compatibility)
├── vapi_transcript.html        ← Legacy (kept for compatibility)
├── vercel.json                 ← Vercel configuration
└── .gitignore
```

---

## Deployment Steps

### Option 1: Vercel CLI (Recommended)

#### Prerequisites
```bash
# Install Vercel CLI globally
npm install -g vercel
```

#### Deploy
```bash
# Navigate to vapi-static folder
cd f:\CTC_HEALTH\Projects\Evaluation_Cycle\vapi-static

# Login to Vercel (first time only)
vercel login

# Deploy to production
vercel --prod
```

#### Output
After deployment, you'll get a URL like:
```
https://vapi-static-xxxxx.vercel.app
```

---

### Option 2: Vercel Dashboard (GUI)

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Set **Root Directory** to `vapi-static`
5. Click **Deploy**

---

### Option 3: GitHub Integration (Auto-Deploy)

1. Push your code to GitHub
2. Connect your repo to Vercel
3. Set root directory to `vapi-static`
4. Every push to main branch auto-deploys

```bash
# Push changes to trigger auto-deploy
git add .
git commit -m "Update VAPI widgets"
git push origin main
```

---

## Configure Your App

After deployment, update your `.env` file with the Vercel URL:

```env
# Before (local development)
VAPI_STATIC_URL=http://localhost:8080

# After (production)
VAPI_STATIC_URL=https://your-project.vercel.app
```

---

## Vercel Configuration

The `vercel.json` file configures the deployment:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "*.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        }
      ]
    }
  ]
}
```

---

## Verify Deployment

After deploying, test by visiting:

```
https://your-project.vercel.app/vapi_combined_widget.html
```

You should see the call widget with transcript area.

---

## Updating After Changes

Whenever you modify the HTML files:

1. **Copy updated files to vapi-static/**
   ```powershell
   Copy-Item -Path "vapi_combined_widget.html" -Destination "vapi-static\" -Force
   ```

2. **Redeploy**
   ```bash
   cd vapi-static
   vercel --prod
   ```

   Or if using GitHub integration, just push:
   ```bash
   git add .
   git commit -m "Update widget"
   git push
   ```

---

## Troubleshooting

### "Microphone access denied"
- Make sure the Vercel URL uses HTTPS
- Check browser permissions for microphone

### "VAPI not initialized"
- Verify VAPI_PUBLIC_KEY and ASSISTANT_ID are correct in the HTML file
- Check browser console for errors

### Widget not loading in Streamlit
- Verify VAPI_STATIC_URL in `.env` matches your Vercel deployment URL
- Make sure the URL doesn't have a trailing slash

### CORS errors
- The `vercel.json` includes CORS headers
- If issues persist, check that headers are being applied

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `vercel login` | Authenticate with Vercel |
| `vercel` | Deploy to preview URL |
| `vercel --prod` | Deploy to production |
| `vercel ls` | List deployments |
| `vercel logs` | View deployment logs |
| `vercel rm <url>` | Remove a deployment |
