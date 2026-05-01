# Contributing to VoteWise AI

Thank you for your interest in contributing! Please follow these guidelines.

---

## 🛠️ Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/votewise-ai.git
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS / Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_google_ai_api_key
FIREBASE_KEY=your_firebase_service_account_json_string
```

> ⚠️ Never commit `.env` or `serviceAccountKey.json` — both are in `.gitignore`.

### 5. Run the app locally
```bash
python app.py
```
Visit `http://127.0.0.1:5000`.

---

## 🧪 Running Tests

```bash
pytest
```

Or with verbose output:
```bash
pytest -v
```

All tests are in `test_app.py`. They use Flask's built-in test client — no external services required for rule-based tests.

---

## 📐 Coding Standards

- **Python 3.11** target (pinned in `.python-version`)
- Follow **PEP 8** for formatting
- Add **docstrings** to all new functions
- Keep functions **focused** — one responsibility per function
- All secrets via **environment variables only** — never hardcode keys
- Wrap external API calls (`genai`, `firestore`) in `try/except`

---

## 🔀 Submitting Changes

1. Create a feature branch: `git checkout -b feature/your-change`
2. Make your changes following the coding standards above
3. Run `pytest` and confirm all tests pass
4. Submit a pull request with a clear description

---

## 🔒 Security Notes

- Do **not** add new routes without rate limiting
- Do **not** log sensitive user data
- Do **not** expose internal errors to API responses
