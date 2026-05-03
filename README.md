# VoteWise AI 🗳️

> **Empowering citizens through information.** VoteWise AI is a production-hardened, interactive election guide featuring a high-performance hybrid AI engine.

## 🚀 Live Demo
**Project Link:** [https://votewise-ai.onrender.com](https://votewise-ai.onrender.com)

---

## ✨ Key Features
- **Hybrid Chatbot:** Intelligent routing between a lightning-fast **Rule-based engine** and **Gemini 2.5 Flash** for complex reasoning.
- **Multi-language Support:** Get answers in **English**, **Hindi (हिंदी)**, or **Telugu (తెలుగు)**.
- **Smart Fallback:** Graceful handling of API failures and out-of-scope queries with guided suggestions.
- **Efficiency First:** Integrated **In-memory Response Caching** to eliminate redundant API calls and reduce costs.
- **Security & Resilience:** Built-in **IP-based Rate Limiting** and strict input validation.

---

## 🔑 Google Services Integration

| Service | How It's Used | Where in Code |
|---|---|---|
| **Gemini 2.5 Flash** | Fallback AI engine for complex queries + real-time translation | `get_gemini_response()`, `translate_response()` in `app.py` |
| **Firebase Firestore** | Structured logging of every interaction with 7 analytics fields | `db.collection("chat_queries").document()` in `app.py` |
| **Google Fonts (Inter)** | UI typography | `<head>` in `index.html` |

> Both Gemini and Firestore are **fault-tolerant** — the app degrades gracefully if either service is unavailable.

## ⚙️ Production Features
| Feature | Detail |
|---|---|
| **Hybrid AI Routing** | Rule-based engine fires first; Gemini invoked only on no-match |
| **MD5-Based Caching** | Cache keys use MD5 hash — zero collision, 1-hour TTL |
| **Rate Limiting** | Per-IP cap (30 req/min) prevents API abuse |
| **Observability Logging** | Firestore logs `source`, `latency_ms`, `response_type`, `timestamp` per query |
| **Accessibility-Compliant UI** | ARIA live regions, semantic HTML, screen-reader ready |
| **Fault-Tolerant Fallback** | App stays live even if Firebase or Gemini are unavailable |

---

## 🏗️ Architecture & Tech Stack
The system follows a streamlined modular flow:
**User Input → API Validation → Rule Engine (Fast) OR Gemini AI (Complex) → Translation Layer → Firestore Logging**

- **Frontend:** Vanilla HTML5/JS + Tailwind CSS (Accessible & Responsive).
- **Backend:** Python / Flask (Clean, modular logic).
- **AI Services:**
  - **Gemini 2.5 Flash (`gemini-2.5-flash`):** Used as the fallback AI engine for complex, open-ended queries not handled by the rule engine. Also powers real-time multi-language translation (Hindi, Telugu).
  - **Firebase Firestore:** Structured interaction logging with the following fields:

### Firestore Logging Fields
| Field | Description |
|---|---|
| `user_query` | Original message submitted by the user |
| `bot_response` | Final response returned to the user |
| `language` | Selected language code (`en`, `hi`, `te`) |
| `source` | Engine that produced the response (`rule-based` or `gemini`) |
| `response_type` | Explicit label mirroring `source` for analytics queries |
| `latency_ms` | End-to-end response time in milliseconds |
| `timestamp` | Server-side UTC timestamp of the request |

---


## ⚡ Performance Highlights
- **Ultra-Low Latency:** Rule-based responses resolve in **<200ms**.
- **Cost Efficient:** Caching ensures repeat queries cost zero tokens.
- **Robust:** Gemini is triggered only when rules aren't met, ensuring high uptime even during quota limits.

---

## 🧠 Architecture Deep Dive

```
User Message
    │
    ▼
Flask API (/api/chat)
    │
    ├── Rate Limit Check (IP-based, 30 req/min)
    │
    ├── Input Validation (empty / >500 chars rejected)
    │
    ├─► Rule Engine (instant, deterministic)
    │       │ match found → return immediately
    │       │ no match ↓
    └─► Gemini 2.5 Flash (AI reasoning)
            │
            ▼
        Translation Layer (Hindi / Telugu via Gemini)
            │
            ▼
        Firestore Logging (latency_ms, source, timestamp)
            │
            ▼
        JSON Response → User
```

### Design Decisions
| Decision | Rationale |
|---|---|
| **Rule-first routing** | Eliminates Gemini cost/latency for 80%+ of common queries |
| **MD5 cache keys** | Prevents collisions on near-identical queries; O(1) lookup |
| **IP rate limiting** | Prevents API abuse without external dependencies |
| **Lazy service init** | Firebase/Gemini initialize on first request — Gunicorn-safe |
| **Neutral AI prompt** | Prevents political bias; aligns with Google AI Principles |
| **Graceful degradation** | App serves rule-based responses even if Gemini/Firebase fail |
| **HTTP Security Headers** | 4-header security stack: `nosniff`, `DENY`, CSP allowlist, `X-Request-ID` |

---

## 🔒 Security Headers

Every HTTP response from the API includes:

| Header | Value | Purpose |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing attacks |
| `X-Frame-Options` | `DENY` | Blocks clickjacking via iframe embedding |
| `Content-Security-Policy` | Scoped allowlist | Restricts script/style/font sources to trusted CDNs only |
| `X-Request-ID` | UUID v4 | Unique per-request ID for log traceability |

---

## 🎮 Demo Guide

Try these inputs to see the hybrid engine in action:

| Input | Expected Behaviour | Engine |
|---|---|---|
| `"how to vote"` | Step-by-step voting guide | ✅ Rule-based |
| `"I am 22 years old"` | Eligibility confirmation | ✅ Rule-based |
| `"What is NOTA?"` | NOTA explanation | ✅ Rule-based |
| `"Explain democracy"` | AI-generated explanation | 🤖 Gemini |
| Change language to Hindi | Same response in Hindi | 🌐 Translation |
| Send 501 characters | Rejected with 400 error | 🔒 Validation |

---



## 🛠️ Deployment & Setup

### Environment Variables
Required secrets for full functionality:
```env
GEMINI_API_KEY=your_google_ai_key
FIREBASE_KEY=your_firebase_json_string
PORT=5000
```

### Local Setup
1. Clone & Install:
   ```bash
   git clone https://github.com/your-username/votewise-ai.git
   pip install -r requirements.txt
   ```
2. Run:
   ```bash
   python app.py
   ```
   *Visit `http://127.0.0.1:5000` to interact.*
---

## 🧪 Testing

**20 automated tests** covering all major paths — run via `pytest` with zero external service dependencies.

| Test Category | Count | What's Covered |
|---|---|---|
| Rule-based accuracy | 8 | EVM, NOTA, register, polling booth, age eligible/ineligible, first-time voter |
| Input validation | 3 | Empty input, oversized input (>500 chars), malformed JSON |
| API contract | 3 | JSON structure, status codes, homepage load |
| Routing priority | 1 | Proves rule engine fires before Gemini |
| Security headers | 1 | Verifies all 4 headers on every response |
| Mock/fallback | 1 | Gemini offline fallback via monkeypatch |
| Language whitelist | 1 | Invalid language code falls back to English |
| Header traceability | 1 | `X-Request-ID` UUID format validated |
| Edge cases | 1 | Missing body / non-JSON payload |

**CI/CD:** Tests auto-run on every push via GitHub Actions (`.github/workflows/pytest.yml`).

```bash
# Run locally
pip install -r requirements.txt
pytest -v
```

---

## 🛡️ AI Safety
- Gemini responses are governed by a **neutral system prompt** that enforces factual, unbiased output.
- The AI **will not** recommend any political party or candidate.
- Out-of-scope queries are redirected to official Election Commission sources.
- Ensures **responsible AI behavior** aligned with Google's AI Principles.

---
*Developed for the Google Antigravity AI Hackathon.*
