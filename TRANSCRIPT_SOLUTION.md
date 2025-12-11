# Transcript Display Solution

## The Problem

We had **unstable transcript display** - messages would appear and disappear, causing a flickering/unstable user experience.

---

## Root Cause: Cross-Iframe Communication

### Original Architecture (Problematic)

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit App                           │
│                                                              │
│  ┌─────────────────────┐        ┌─────────────────────┐     │
│  │     iframe 1        │   ?    │      iframe 2       │     │
│  │   Call Widget       │───────▶│    Transcript       │     │
│  │                     │        │                     │     │
│  │ - VAPI SDK          │        │ - Needs transcript  │     │
│  │ - Receives events   │        │   data from iframe1 │     │
│  │ - Has transcript    │        │                     │     │
│  └─────────────────────┘        └─────────────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

The `?` represents the **communication problem** - there's no reliable way to send data between sibling iframes.

### Methods We Tried (All Failed or Were Unstable)

| Method | Issue |
|--------|-------|
| **localStorage + Polling** | Caused flickering. Polling every 50-300ms caused race conditions and unnecessary DOM rebuilds. |
| **localStorage + storage event** | The `storage` event only fires in OTHER windows/tabs, not between iframes in the same page. |
| **BroadcastChannel API** | Didn't work reliably across Streamlit's sandboxed iframes. |
| **postMessage to parent** | Parent (Streamlit) doesn't relay messages to sibling iframes. We can't modify Streamlit's behavior. |

### Why localStorage Caused Flickering

1. **Polling interval** - Even at 50ms, there were timing gaps
2. **Full DOM rebuild** - Each poll rebuilt the entire transcript HTML
3. **Animation replay** - CSS animations triggered on every rebuild
4. **Race conditions** - Call widget clearing transcript while transcript iframe was reading

---

## The Solution: Single Combined Widget

### New Architecture (Stable)

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit App                           │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 Single iframe                        │    │
│  │                                                      │    │
│  │  ┌──────────────┐    ┌────────────────────────┐     │    │
│  │  │ Call Widget  │    │     Transcript         │     │    │
│  │  │              │───▶│                        │     │    │
│  │  │ - VAPI SDK   │    │ - Direct DOM updates   │     │    │
│  │  │ - Events     │    │ - No communication     │     │    │
│  │  └──────────────┘    │   overhead             │     │    │
│  │                      └────────────────────────┘     │    │
│  │                                                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### How It Works

1. **Single HTML file** (`vapi_combined_widget.html`) contains both:
   - Call controls (avatar, buttons, timer)
   - Transcript display area

2. **VAPI SDK** receives transcript events:
   ```javascript
   vapi.on('message', (message) => {
       if (message.type === 'transcript' && message.transcriptType === 'final') {
           addMessage(message.role, message.transcript);
       }
   });
   ```

3. **Direct DOM update** - no localStorage, no postMessage, no polling:
   ```javascript
   function addMessage(role, content) {
       const div = document.createElement('div');
       div.className = `message message-${roleClass}`;
       div.innerHTML = `...`;
       transcriptContainer.appendChild(div);  // Direct append!
   }
   ```

### Key Benefits

| Before | After |
|--------|-------|
| 2 iframes | 1 iframe |
| localStorage polling | Direct function call |
| Race conditions | Synchronous updates |
| Flickering | Stable |
| Complex communication | No communication needed |

---

## Files Changed

### Created
- `vapi_combined_widget.html` - Combined call + transcript widget

### Modified
- `app.py` - Changed from 3 columns to 2 columns layout:
  ```python
  # Before: 3 columns
  col_feedback, col_call, col_transcript = st.columns([1, 1.2, 1.2])
  
  # After: 2 columns
  col_feedback, col_call = st.columns([1, 2.5])
  ```

### Deprecated (can be removed)
- `vapi_call_widget.html` - Old separate call widget
- `vapi_transcript.html` - Old separate transcript viewer

---

## Lesson Learned

> **When you need to share data between iframes, consider combining them into a single iframe instead of trying to solve the cross-iframe communication problem.**

Cross-iframe communication is inherently complex due to:
- Same-origin policy restrictions
- Sandboxed iframe limitations (especially in frameworks like Streamlit)
- Timing/race conditions with polling approaches
- Browser security features

The simplest solution is often to **eliminate the need for communication** by keeping related functionality together.
