# Deployment Guide

This guide explains how to deploy the Evaluation Cycle Streamlit application with VAPI voice call integration.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Deployment Challenges](#deployment-challenges)
3. [Deployment Options](#deployment-options)
4. [Recommended Approach](#recommended-approach-hybrid-deployment)
5. [Step-by-Step Instructions](#step-by-step-instructions)
6. [Environment Variables](#environment-variables)
7. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The application consists of three main components:

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit App (app.py)                   │
│  ┌─────────────┬─────────────────────┬─────────────────┐   │
│  │  Feedback   │    Call Widget      │   Transcript    │   │
│  │  Column     │    (iframe)         │   (iframe)      │   │
│  │             │                     │                 │   │
│  │  [Text]     │  ┌───────────────┐  │  ┌───────────┐  │   │
│  │  [Save]     │  │ vapi_call_    │  │  │ vapi_     │  │   │
│  │             │  │ widget.html   │  │  │ transcript│  │   │
│  │             │  └───────────────┘  │  │ .html     │  │   │
│  │             │                     │  └───────────┘  │   │
│  └─────────────┴─────────────────────┴─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   VAPI Cloud    │
                    │   (Voice AI)    │
                    └─────────────────┘
```

**Key Files:**
- `app.py` - Main Streamlit application
- `vapi_call_widget.html` - VAPI call controls and connection
- `vapi_transcript.html` - Live transcript display
- `.env` - Environment variables (API keys)

---

## Deployment Challenges

### Why Standard Streamlit Cloud Deployment Won't Work

1. **Local HTTP Server Requirement**
   - The app starts a Python HTTP server on port 8080
   - Streamlit Cloud doesn't allow custom background processes
   - Only the main Streamlit port is exposed

2. **localhost References**
   - Iframes reference `http://localhost:8080/...`
   - These URLs don't exist in cloud environments

3. **Browser Security (Microphone Access)**
   - Browsers require HTTPS for microphone permissions in production
   - Iframe sandbox restrictions block microphone access
   - This is why we serve HTML files from a separate origin

4. **Cross-Origin Communication**
   - The call widget and transcript use `localStorage` to share data
   - Both must be on the same origin for this to work

---

## Deployment Options

| Option | Complexity | Cost | Best For |
|--------|------------|------|----------|
| **Hybrid (Recommended)** | Low | Free | Most users |
| VPS/Cloud VM | Medium | $5-20/mo | Full control |
| Docker + Cloud Run | Medium | Pay-per-use | Scalability |
| Heroku | Medium | Free-$25/mo | Simple PaaS |

---

## Recommended Approach: Hybrid Deployment

Deploy the components separately:

```
┌────────────────────────┐     ┌─────────────────────────┐
│   Streamlit Cloud      │     │   Vercel / Netlify      │
│   (streamlit.io)       │     │   (Static Hosting)      │
│                        │     │                         │
│   - app.py             │────▶│   - vapi_call_widget.html
│   - Main UI            │     │   - vapi_transcript.html│
│   - Bot management     │     │                         │
└────────────────────────┘     └─────────────────────────┘
         │                                  │
         └──────────────┬───────────────────┘
                        ▼
              ┌─────────────────┐
              │   VAPI Cloud    │
              └─────────────────┘
```

**Benefits:**
- Free hosting on both platforms
- HTTPS enabled automatically (required for microphone)
- No server management
- Easy updates

---

## Step-by-Step Instructions

### Step 1: Deploy Static Files to Vercel

1. **Create a new folder** for static files:
   ```
   vapi-static/
   ├── vapi_call_widget.html
   ├── vapi_transcript.html
   └── vercel.json
   ```

2. **Create `vercel.json`** for CORS headers:
   ```json
   {
     "headers": [
       {
         "source": "/(.*)",
         "headers": [
           { "key": "Access-Control-Allow-Origin", "value": "*" },
           { "key": "Access-Control-Allow-Methods", "value": "GET" }
         ]
       }
     ]
   }
   ```

3. **Deploy to Vercel:**
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Navigate to folder and deploy
   cd vapi-static
   vercel --prod
   ```

4. **Note your deployment URL** (e.g., `https://vapi-static.vercel.app`)

### Step 2: Update app.py for Cloud Deployment

Replace the localhost URLs with your Vercel deployment URL:

```python
# Before (local development)
VAPI_STATIC_BASE = "http://localhost:8080"

# After (production)
VAPI_STATIC_BASE = "https://your-project.vercel.app"
```

**Modify the `render_call_interface` function:**

```python
def render_call_interface(bot_name: str):
    # ... existing code ...
    
    # Use environment variable for flexibility
    static_base = os.getenv('VAPI_STATIC_URL', 'http://localhost:8080')
    
    # Call column
    with col2:
        st.components.v1.html(
            f'''<iframe
                src="{static_base}/vapi_call_widget.html?public_key={VAPI_PUBLIC_KEY}&assistant_id={VAPI_ASSISTANT_ID}&bot_name={bot_name}&avatar_emoji={avatar_emoji}"
                style="width: 100%; height: 550px; border: none;"
                allow="microphone; camera; autoplay"
            ></iframe>''',
            height=570
        )
    
    # Transcript column
    with col3:
        st.components.v1.html(
            f'''<iframe
                src="{static_base}/vapi_transcript.html?bot_name={bot_name}"
                style="width: 100%; height: 550px; border: none;"
            ></iframe>''',
            height=570
        )
```

### Step 3: Remove Local HTTP Server Code

For cloud deployment, remove or conditionally skip the HTTP server startup:

```python
# Add this check at the top
IS_CLOUD = os.getenv('STREAMLIT_CLOUD', 'false').lower() == 'true'

# Modify the server startup
if not IS_CLOUD:
    if 'http_server_started' not in st.session_state:
        start_http_server()
        st.session_state.http_server_started = True
```

### Step 4: Deploy to Streamlit Cloud

1. **Push code to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for cloud deployment"
   git push origin main
   ```

2. **Create `requirements.txt`** (if not exists):
   ```
   streamlit
   python-dotenv
   ```

3. **Go to [share.streamlit.io](https://share.streamlit.io)**

4. **Connect your GitHub repository**

5. **Configure secrets** in Streamlit Cloud dashboard:
   - Go to App Settings → Secrets
   - Add your environment variables:
   ```toml
   VAPI_PUBLIC_KEY = "your_public_key"
   VAPI_ASSISTANT_ID = "your_assistant_id"
   VAPI_STATIC_URL = "https://your-project.vercel.app"
   STREAMLIT_CLOUD = "true"
   ```

6. **Deploy!**

---

## Environment Variables

### Local Development (`.env`)

```env
VAPI_PUBLIC_KEY=your_vapi_public_key
VAPI_API_KEY=your_vapi_private_key
VAPI_ASSISTANT_ID=your_assistant_id
```

### Streamlit Cloud (Secrets)

```toml
VAPI_PUBLIC_KEY = "your_vapi_public_key"
VAPI_ASSISTANT_ID = "your_assistant_id"
VAPI_STATIC_URL = "https://your-project.vercel.app"
STREAMLIT_CLOUD = "true"
```

---

## Alternative: Deploy to VPS

If you prefer full control, deploy to a VPS (DigitalOcean, AWS EC2, etc.):

### Using Docker

1. **Create `Dockerfile`:**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501 8080
   
   CMD ["sh", "-c", "python -m http.server 8080 & streamlit run app.py --server.port=8501"]
   ```

2. **Create `docker-compose.yml`:**
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "8501:8501"
         - "8080:8080"
       env_file:
         - .env
   ```

3. **Deploy:**
   ```bash
   docker-compose up -d
   ```

### Using nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /vapi-static/ {
        alias /path/to/vapi-static-files/;
    }
}
```

---

## Troubleshooting

### Microphone Not Working in Production

**Cause:** Browser requires HTTPS for microphone access.

**Solution:** Ensure your static file host (Vercel/Netlify) uses HTTPS. Both do this by default.

### Transcript Not Updating

**Cause:** localStorage doesn't work across different origins.

**Solution:** Both `vapi_call_widget.html` and `vapi_transcript.html` must be served from the same domain.

### CORS Errors

**Cause:** Cross-origin requests blocked.

**Solution:** Add CORS headers to your static file host (see `vercel.json` example above).

### "Connecting..." Forever

**Cause:** Usually a VAPI key issue or network problem.

**Solution:**
1. Verify `VAPI_PUBLIC_KEY` and `VAPI_ASSISTANT_ID` are correct
2. Check browser console for errors
3. Ensure the assistant exists in your VAPI dashboard

---

## Quick Reference

| Environment | Streamlit URL | Static Files URL |
|-------------|---------------|------------------|
| Local Dev | `http://localhost:8501` | `http://localhost:8080` |
| Production | `https://your-app.streamlit.app` | `https://your-project.vercel.app` |

---

## Support

- **VAPI Documentation:** https://docs.vapi.ai
- **Streamlit Cloud Docs:** https://docs.streamlit.io/streamlit-cloud
- **Vercel Docs:** https://vercel.com/docs

