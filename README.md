# VoteWise AI 🗳️

> **Empowering citizens through information.** VoteWise AI is a premium, full-stack interactive assistant designed to simplify the election process for voters everywhere.

## 🌟 Demo
**Live Project Link:** [https://votewise-ai.onrender.com]

---

## 📖 Project Overview
VoteWise AI tackles the critical issue of voter education. Many citizens—especially first-time voters—are unaware of the step-by-step election process, eligibility criteria, and important election jargon (like EVM and NOTA). VoteWise AI bridges this gap with a polished, accessible, and simple-to-use platform featuring an intelligent chatbot.

---

## 🏗️ System Design
The application is designed to be highly secure, lightning-fast, and deeply modular:
- **Frontend (View):** HTML5, Vanilla JavaScript, and Tailwind CSS (via CDN for zero-build overhead). 
- **Backend (Controller):** Python & Flask for rapid, lightweight API routing and AI logic processing.
- **Database (Model):** Firebase Firestore (NoSQL) for securely and asynchronously logging user queries and interactions.

*(The entire application is engineered to stay under 1MB, ensuring maximum performance even on low-bandwidth networks.)*

---

## 🤖 Prompt Engineering Strategy
VoteWise AI utilizes a carefully crafted rule-based prompt logic system optimized for clarity, engagement, and safety:
- **Role-based Logic:** The bot consistently assumes the role of an objective, helpful election guide.
- **Context-Aware Behavior:** It recognizes specific intents (like "first-time voter" or "documents required") and provides tailored, encouraging advice.
- **Structured Responses:** Every response is formatted into bite-sized, bulleted, or numbered step-by-step structures, maximizing readability.
- **Smart Fallback:** When an intent is not recognized, the bot gracefully guides the user back on track by explicitly suggesting specific clickable-style queries.

---

## ✨ Why This Stands Out
- **Lightweight & Blazing Fast:** Zero heavy API dependencies, meaning instantaneous response times and an overall project size of `<1MB`.
- **Premium UX/UI:** Features micro-interactions like message fade-ins, "Typing..." indicators, auto-scrolling chat, scrollspy navigation, and soft shadows.
- **Accessibility First:** Fully navigable via keyboard, strict semantic HTML, visible focus rings, and high contrast text ensures everyone can participate.
- **Built using Google Antigravity:** Engineered with an AI-first collaborative approach, prioritizing clean code and rapid iteration.

---

## 🌍 Real-World Impact
- **Helps First-Time Voters:** Breaks down an intimidating democratic process into an easy-to-follow, 5-step journey.
- **Improves Civic Awareness:** Defines crucial election jargon, empowering citizens to make informed decisions.
- **Reduces Confusion:** Consolidates everything—from checking eligibility based on age to understanding the timeline—into one single, cohesive interface.

---

## 🚀 Setup Instructions
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/votewise-ai.git
   cd votewise-ai
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Application**:
   ```bash
   python app.py
   ```
4. **Access the Web App**: Open your browser and go to `http://127.0.0.1:5000`.

### 🔒 Firebase Integration (Optional but recommended)
To enable secure chat logging:
1. Create a Firebase project and a Firestore Database.
2. Generate a Service Account private key (`serviceAccountKey.json`) and place it in the root directory.
3. Ensure the `.env` file points to it:
   ```env
   FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json
   ```
*(Note: The app will run gracefully even without Firebase credentials, automatically disabling database writes).*
