import os
import json
import re
import time
import hashlib
import uuid
from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_security_headers(response):
    """Attach traceability and security headers to every response."""
    response.headers['X-Request-ID'] = str(uuid.uuid4())
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "connect-src 'self'"
    )
    return response

# Security: In-memory cache & Rate limiting state
response_cache = {}
CACHE_EXPIRY = 3600 # 1 hour
IP_REQUESTS = {}
RATE_LIMIT_WINDOW = 60 # 1 minute
MAX_REQUESTS_PER_MINUTE = 30
 
# Global State
firebase_initialized = False
db = None
gemini_initialized = False
gemini_model = None

# Safe, idempotent service initialization (called inside routes, NOT at import time)
def init_services():
    """Initialize Firebase and Gemini lazily. Safe to call multiple times."""
    global firebase_initialized, db, gemini_initialized, gemini_model

    # Initialize Firebase safely
    if firebase_initialized is False:
        try:
            firebase_key = os.environ.get("FIREBASE_KEY")
            if firebase_key:
                firebase_dict = json.loads(firebase_key)
                cred = credentials.Certificate(firebase_dict)
                if not firebase_admin._apps:
                    firebase_admin.initialize_app(cred)
                db = firestore.client()
                firebase_initialized = True
                print("Firebase initialized successfully")
            else:
                print("FIREBASE_KEY not found. Running without Firebase.")
                firebase_initialized = "OFFLINE"
        except Exception as e:
            print(f"Firebase init error: {e}")
            firebase_initialized = "FAILED"

    # Initialize Gemini safely
    if gemini_initialized is False:
        try:
            gemini_api_key = os.environ.get("GEMINI_API_KEY")
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
                gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                gemini_initialized = True
                print("Gemini initialized successfully")
            else:
                print("GEMINI_API_KEY missing. AI features disabled.")
                gemini_initialized = "OFFLINE"
        except Exception as e:
            print(f"Gemini init error: {e}")
            gemini_initialized = "FAILED"


def get_rule_based_response(user_message):
    """
    Handles standard voting queries using hardcoded rules for maximum efficiency.
    Returns the response string or None if no rule matches.
    """
    message = user_message.lower()
    
    # Age/Eligibility detection using strict regex
    age_match = re.search(r"(?:i am|i'm|my age is|age is)\s*(\d+)|(\d+)\s*years old", message)
    is_explain_prompt = "explain" in message and "like i am" in message
    
    if age_match and not is_explain_prompt:
        age_str = age_match.group(1) or age_match.group(2)
        if age_str:
            age = int(age_str)
            state_match = re.search(r'from ([a-zA-Z\s]+)', message)
            state = state_match.group(1).strip() if state_match else "your state"
            
            if age >= 18:
                return (
                    f"Great news! Since you are {age}, you are fully eligible to vote in {state.title()}.\n\n"
                    "Next Steps:\n"
                    "1. Check if you are on the electoral roll.\n"
                    "2. Register to vote if you haven't already.\n"
                    "3. Find your polling booth."
                )
            else:
                return f"Since you are {age}, you must wait until you are 18 to be eligible to vote. However, it's great that you are learning about the process early!"

    # Keyword mapping
    if "first time" in message or "new" in message or "beginner" in message:
        return (
            "Welcome to the democratic process! Here is a step-by-step guide for beginners:\n"
            "1. Check eligibility: Ensure you are 18+ and a citizen.\n"
            "2. Register: Apply for your Voter ID card online or offline.\n"
            "3. Get voter ID: Keep your Voter ID (EPIC) ready.\n"
            "4. Visit polling booth: Find your assigned station before Election Day.\n"
            "5. Cast vote using EVM: Follow instructions at the booth to cast your vote securely."
        )
    elif "how to vote" in message:
        return (
            "Here is how you cast your vote:\n"
            "1. Enter the polling station and show your ID to the polling officer.\n"
            "2. Proceed to the voting compartment.\n"
            "3. Press the blue button on the Electronic Voting Machine (EVM) next to your chosen candidate.\n"
            "4. Wait for the beep sound to confirm your vote was recorded."
        )
    elif "register" in message:
        return (
            "To register to vote:\n"
            "1. Visit the official Election Commission Voter Portal.\n"
            "2. Fill out the new voter registration form (usually Form 6).\n"
            "3. Upload a passport-size photo, age proof, and address proof.\n"
            "4. Submit the form and track your application status online."
        )
    elif "evm" in message:
        return (
            "An Electronic Voting Machine (EVM) is used to record votes securely.\n"
            "• It consists of a Control Unit and a Balloting Unit.\n"
            "• It prevents tampering and ensures quick counting of votes."
        )
    elif "nota" in message:
        return (
            "NOTA stands for 'None of the Above'.\n"
            "• It is an option on the EVM for voters who do not wish to vote for any of the listed candidates.\n"
            "• It allows you to exercise your democratic right to vote without compromising your personal choice."
        )
    elif "documents" in message or "id" in message or "proof" in message:
        return (
            "To register for voting, you may need:\n"
            "• Aadhaar Card\n"
            "• Address Proof (Electricity bill / Rental agreement)\n"
            "• Passport size photo\n"
            "• Identity proof"
        )
    elif "where to vote" in message or "polling booth" in message or "location" in message:
        return (
            "To find your polling booth:\n"
            "• Visit the official Election Commission website.\n"
            "• Enter your voter ID (EPIC number) or personal details.\n"
            "• Locate your nearest assigned polling station on the map."
        )
    elif "election process" in message:
        return (
            "The Election Process involves these key phases:\n"
            "1. Voter Registration: Ensure you are on the list.\n"
            "2. Candidate Nomination: Candidates file paperwork.\n"
            "3. Political Campaigning: Candidates share their platforms.\n"
            "4. Voting on Election Day: Citizens cast their ballots.\n"
            "5. Counting of Votes and Results: Officials tally votes and declare winners."
        )
    
    return None # Return None if no rule matched


def get_gemini_response(user_input):
    """
    Handles complex queries by passing them to Gemini.
    Uses caching to avoid redundant API calls.
    """
    if not gemini_initialized:
        return (
            "Try asking:\n"
            "• How to vote\n"
            "• Documents required\n"
            "• First-time voter guide\n"
            "• Where to vote"
        )
    
    # Check cache first using safe MD5 hash
    cache_key = f"gen_{hashlib.md5(user_input.lower().strip().encode()).hexdigest()[:16]}"
    if cache_key in response_cache:
        cached_data = response_cache[cache_key]
        if time.time() - cached_data['time'] < CACHE_EXPIRY:
            return cached_data['text']
            
    prompt = (
        "You are VoteWise AI, a neutral, factual election assistant for Indian voters. "
        "Rules: Do NOT recommend any party or candidate. Do NOT express political opinions. "
        "If asked for political advice, reply: 'I cannot recommend any party or candidate. "
        "Please refer to official Election Commission sources.' "
        "Scope: voting process, eligibility, documents, election awareness. "
        "Style: simple, clear, step-by-step with bullet points. "
        "User query: " + user_input
    )
    
    try:
        response = gemini_model.generate_content(prompt)
        text = response.text.strip()
        # Save to cache
        response_cache[cache_key] = {'text': text, 'time': time.time()}
        return text
    except Exception as e:
        print(f"Gemini generation error: {e}")
        return "I'm having trouble thinking right now. Please try asking about 'how to vote' or 'documents required'."


def translate_response(text, target_language):
    """
    Translates the final bot response into the target language using Gemini.
    Bypasses translation if target is English or Gemini is offline.
    """
    if not gemini_initialized or target_language == 'en':
        return text
        
    lang_map = {
        "hi": "Hindi",
        "te": "Telugu"
    }
    target_lang_name = lang_map.get(target_language, "English")
    
    if target_lang_name == "English":
        return text
        
    # Check cache using safe MD5 hash to prevent long key or collision issues
    cache_key = f"trans_{target_language}_{hashlib.md5(text.encode()).hexdigest()[:16]}"
    if cache_key in response_cache:
        cached_data = response_cache[cache_key]
        if time.time() - cached_data['time'] < CACHE_EXPIRY:
            return cached_data['text']
            
    prompt = (
        f"Translate the following text to {target_lang_name}. "
        "Maintain the exact same formatting, bullet points, and structure. "
        "Only output the translated text, nothing else.\n\n"
        f"Text to translate:\n{text}"
    )
    
    try:
        response = gemini_model.generate_content(prompt)
        translated_text = response.text.strip()
        response_cache[cache_key] = {'text': translated_text, 'time': time.time()}
        return translated_text
    except Exception as e:
        print(f"Gemini translation error: {e}")
        return text # fallback to english gracefully


def check_rate_limit(ip):
    """Lightweight rate limiting to prevent API abuse."""
    current_time = time.time()
    
    # Clean up old records
    if ip in IP_REQUESTS:
        IP_REQUESTS[ip] = [t for t in IP_REQUESTS[ip] if current_time - t < RATE_LIMIT_WINDOW]
    else:
        IP_REQUESTS[ip] = []
        
    if len(IP_REQUESTS[ip]) >= MAX_REQUESTS_PER_MINUTE:
        return False
        
    IP_REQUESTS[ip].append(current_time)
    return True


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Main API endpoint for the chatbot.
    Handles rate limiting, validation, hybrid routing, translation, and Firestore logging.
    """
    # 0. Ensure services are ready; start latency clock for observability
    request_start = time.time()
    init_services()

    # 1. Rate Limiting
    client_ip = request.remote_addr
    if not check_rate_limit(client_ip):
        return jsonify({
            "response": "You are sending too many messages. Please wait a moment.",
            "status": "error"
        }), 429
        
    # 2. Input Validation & Sanitization
    try:
        data = request.json
        if not data:
            return jsonify({"response": "Invalid request format.", "status": "error"}), 400
            
        user_message = str(data.get("message", "")).strip()
        language = str(data.get("language", "en")).strip().lower()
        # Whitelist valid languages — reject unexpected values to prevent prompt injection
        if language not in ("en", "hi", "te"):
            language = "en"
        
        if not user_message:
            return jsonify({"response": "Message cannot be empty.", "status": "error"}), 400
            
        if len(user_message) > 500:
            return jsonify({"response": "Message is too long. Please keep it under 500 characters.", "status": "error"}), 400
            
    except Exception as e:
        return jsonify({"response": "An unexpected error occurred processing your input.", "status": "error"}), 400
        
    # 3. Smart Hybrid Routing: rule-based runs first to minimise API cost and latency
    source = "rule-based"
    try:
        bot_response = get_rule_based_response(user_message)

        # Fall through to Gemini only when no rule matches
        if not bot_response:
            source = "gemini"
            bot_response = get_gemini_response(user_message)
            
        # 4. Translation Layer (Skip if base failed or if English)
        final_response = bot_response
        if language != "en" and "trouble thinking right now" not in bot_response:
            final_response = translate_response(bot_response, language)
            
    except Exception as e:
        print(f"Routing error: {e}")
        return jsonify({
            "response": "I'm currently experiencing high load. Please try again shortly. "
                        "You can also ask about voting eligibility or required documents.",
            "status": "error"
        }), 500
        
    # 5. Firebase Logging — enriched with latency and response_type for observability
    latency_ms = round((time.time() - request_start) * 1000, 2)
    if firebase_initialized is True and db:
        try:
            doc_ref = db.collection("chat_queries").document()
            doc_ref.set({
                "user_query": user_message,
                "bot_response": final_response,
                "language": language,
                "source": source,
                "response_type": source,      # explicit type label for analytics
                "latency_ms": latency_ms,     # end-to-end request latency
                "timestamp": firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            print(f"Failed to write to Firebase: {e}")
                
    # 6. Return Structured Output
    return jsonify({
        "response": final_response,
        "status": "success"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
