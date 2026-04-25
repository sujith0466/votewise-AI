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

## 🏗️ Architecture & Tech Stack
The system follows a streamlined modular flow:
**User Input → API Validation → Rule Engine (Fast) OR Gemini AI (Complex) → Translation Layer → Firestore Logging**

- **Frontend:** Vanilla HTML5/JS + Tailwind CSS (Accessible & Responsive).
- **Backend:** Python / Flask (Clean, modular logic).
- **AI Services:** 
  - **Gemini API:** Powers advanced reasoning and real-time translation.
  - **Firebase Firestore:** Securely logs interactions (`query`, `response`, `source`, `timestamp`).

---

## ⚡ Performance Highlights
- **Ultra-Low Latency:** Rule-based responses resolve in **<200ms**.
- **Cost Efficient:** Caching ensures repeat queries cost zero tokens.
- **Robust:** Gemini is triggered only when rules aren't met, ensuring high uptime even during quota limits.

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
