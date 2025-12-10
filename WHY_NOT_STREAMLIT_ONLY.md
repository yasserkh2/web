# Why Streamlit Alone Is Not Enough

This document explains why we need Vercel (or another static host) in addition to Streamlit Cloud for this project.

---

## The Short Answer

**Streamlit blocks microphone access in embedded HTML.**

We need voice calls → Voice calls need microphone → Microphone is blocked in Streamlit → We need external hosting.

---

## The Technical Explanation

### How Streamlit Embeds HTML

When you use `st.components.v1.html()` or `st.components.v1.iframe()`, Streamlit wraps your content in a **sandboxed iframe**:

```html
<!-- What Streamlit generates internally -->
<iframe 
    sandbox="allow-scripts allow-same-origin"
    srcdoc="<your HTML here>"
>
</iframe>
```

### What the Sandbox Does

The `sandbox` attribute is a **security feature** that restricts what the iframe can do:

| Permission | Allowed? | Impact |
|------------|----------|--------|
| Run JavaScript | ✅ Yes | Scripts work |
| Access same-origin | ✅ Yes | Basic features work |
| **Access microphone** | ❌ **No** | Voice calls fail |
| **Access camera** | ❌ **No** | Video calls fail |
| Access location | ❌ No | GPS blocked |
| Open popups | ❌ No | Popups blocked |

### The Missing Permission

To allow microphone access, the iframe needs:

```html
<iframe allow="microphone" ...>
```

**Streamlit does NOT add this attribute**, and we cannot modify it.

---

## What We Tried (And Why It Failed)

### Attempt 1: Inline HTML

```python
st.components.v1.html("""
    <script>
        navigator.mediaDevices.getUserMedia({audio: true})
        // ❌ BLOCKED: NotAllowedError
    </script>
""")
```

**Result:** Browser blocks microphone request.

### Attempt 2: Streamlit Static Folder

```python
# Serve from static folder
st.components.v1.iframe("/_app/static/vapi_call.html")
```

**Result:** Still embedded in sandboxed iframe → Still blocked.

### Attempt 3: VAPI Official Widget

```html
<vapi-widget assistant-id="..."></vapi-widget>
```

**Result:** Widget loads, but microphone blocked in iframe.

### Attempt 4: Local HTTP Server (What Works Locally)

```python
# Start HTTP server on port 8080
# Embed iframe pointing to localhost:8080
```

**Result:** ✅ Works locally! But...
- Streamlit Cloud can't run background processes
- Can't expose custom ports
- `localhost` doesn't exist in cloud

---

## The Solution

### External Static Hosting

Host the voice call HTML files on a service that:
1. Serves files directly (not in iframe)
2. Supports HTTPS
3. Allows microphone permissions

```
┌─────────────────────────────────────────────────────────────┐
│                     HOW IT WORKS                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  Streamlit   │ iframe  │   Vercel     │                 │
│  │  Cloud       │────────►│   (HTTPS)    │                 │
│  │              │         │              │                 │
│  │  Main App    │         │  HTML files  │                 │
│  └──────────────┘         └──────┬───────┘                 │
│                                  │                          │
│                                  ▼                          │
│                           ┌──────────────┐                 │
│                           │   Browser    │                 │
│                           │              │                 │
│                           │  🎤 Allowed  │                 │
│                           └──────────────┘                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Why Vercel Works

| Feature | Streamlit | Vercel |
|---------|-----------|--------|
| Hosts HTML | ✅ (in iframe) | ✅ (direct) |
| HTTPS | ✅ | ✅ |
| Microphone allowed | ❌ | ✅ |
| Custom headers | ❌ | ✅ |
| Free tier | ✅ | ✅ |

---

## Browser Security Explained

### Why Browsers Block Microphone in Iframes

Imagine a malicious website:

```html
<iframe src="https://evil-site.com/steal-audio.html"></iframe>
```

If iframes had unrestricted microphone access:
- Any website could embed hidden iframes
- Those iframes could record your audio
- You'd never know

**Solution:** Browsers require explicit permission via `allow="microphone"`.

### The Permission-Policy Header

When Vercel serves our HTML, we can add headers:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Permissions-Policy", "value": "microphone=(*)" }
      ]
    }
  ]
}
```

This tells the browser: "This page is allowed to request microphone."

---

## Could Streamlit Fix This?

### What Streamlit Would Need To Do

1. Add `allow="microphone camera"` to component iframes
2. Modify sandbox to include `allow-microphone`
3. Or provide a "trusted HTML" mode

### Why They Haven't

- **Security risk:** Opening microphone access could be abused
- **Not core use case:** Streamlit focuses on data apps, not media
- **Complexity:** Would need per-component permissions

### Feature Request

This has been requested by the community:
- https://github.com/streamlit/streamlit/issues/1291
- As of now, no built-in solution

---

## Summary

| Question | Answer |
|----------|--------|
| Can Streamlit host HTML? | ✅ Yes |
| Can Streamlit run our app? | ✅ Yes |
| Can voice calls work in Streamlit? | ❌ No |
| Why not? | Browser blocks microphone in sandboxed iframes |
| Is this Streamlit's fault? | ❌ No, it's browser security |
| Can Streamlit fix it? | Possibly, but not yet implemented |
| Solution? | Host voice HTML on Vercel/Netlify |

---

## Visual Comparison

### Streamlit Only (❌ Doesn't Work)

```
User → Streamlit → Sandboxed Iframe → HTML → 🎤 BLOCKED
```

### Streamlit + Vercel (✅ Works)

```
User → Streamlit → Iframe → Vercel URL → HTML → 🎤 ALLOWED
                              ↑
                    (served with proper permissions)
```

---

## What We Deploy Where

| Component | Platform | Reason |
|-----------|----------|--------|
| `app.py` (main app) | Streamlit Cloud | Python, UI, logic |
| `vapi_call_widget.html` | Vercel | Needs microphone |
| `vapi_transcript.html` | Vercel | Same origin as widget |
| Database | Supabase | Already cloud-hosted |
| Voice AI | VAPI | Already cloud-hosted |

---

## Cost Impact

| Service | Cost |
|---------|------|
| Streamlit Cloud | Free |
| Vercel | Free |
| **Total** | **$0/month** |

Adding Vercel doesn't cost anything extra.

---

## Alternatives to Vercel

If you don't want to use Vercel:

| Service | Also Works? | Notes |
|---------|-------------|-------|
| Netlify | ✅ Yes | Similar to Vercel |
| GitHub Pages | ✅ Yes | Free, slightly slower |
| Cloudflare Pages | ✅ Yes | Fast CDN |
| AWS S3 + CloudFront | ✅ Yes | More complex setup |
| Your own server | ✅ Yes | Full control |

Any static hosting with HTTPS will work.

---

## Conclusion

**Streamlit is excellent for the main application**, but browser security prevents microphone access in embedded content. This is not a Streamlit bug—it's intentional browser security.

The solution is simple: host the 2 voice HTML files on any static host (Vercel recommended), and everything works perfectly.

**Total deployment:**
- 1 Streamlit app (main UI + logic)
- 2 HTML files on Vercel (voice calls)
- Same cost: $0

