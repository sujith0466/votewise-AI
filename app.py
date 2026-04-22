import os
import json
import datetime
from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Firebase
firebase_initialized = False
db = None

try:
    firebase_key = os.environ.get("FIREBASE_KEY")
    if firebase_key:
        firebase_dict = json.loads(firebase_key)
        cred = credentials.Certificate(firebase_dict)
    else:
        cred = credentials.Certificate("serviceAccountKey.json")
    
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    firebase_initialized = True
    print("Firebase initialized")
except Exception as e:
    print(f"Failed to initialize Firebase: {e}")

# Rule-based chatbot logic
def get_bot_response(user_message):
    message = user_message.lower()
    
    if "first time voter" in message:
        return (
            "Welcome, first-time voter! Here is how to get started:\n"
            "1. Check if you are eligible (e.g., 18+ years old and a citizen).\n"
            "2. Register to vote online or at your local election office.\n"
            "3. Find your designated polling booth before Election Day.\n"
            "4. Bring a valid photo ID when you go to vote.\n"
            "5. Don't hesitate to ask polling officers for help on the day!"
        )
    elif "how to vote" in message:
        return (
            "Here is how to vote:\n"
            "1. Register as a voter.\n"
            "2. Verify your name in the voter list.\n"
            "3. Visit the polling booth on election day.\n"
            "4. Cast your vote using the EVM or mail-in ballot.\n"
            "5. Confirm your vote was recorded."
        )
    elif "register" in message:
        return (
            "Steps to register to vote:\n"
            "• Visit your local election office or official voter portal online.\n"
            "• Fill out the voter registration form.\n"
            "• Submit valid proof of identity and address.\n"
            "• Check your application status online to ensure you are on the list."
        )
    elif "evm" in message:
        return (
            "EVM stands for Electronic Voting Machine.\n"
            "• It consists of a Control Unit and a Balloting Unit.\n"
            "• You simply press the button next to your chosen candidate's symbol.\n"
            "• It is fast, secure, and speeds up the counting process significantly."
        )
    elif "nota" in message:
        return (
            "NOTA means 'None of the Above'.\n"
            "• It is an option on the EVM for voters who do not wish to vote for any of the listed candidates.\n"
            "• It allows you to exercise your democratic right to vote without compromising your personal choice."
        )
    elif "documents" in message or "id" in message or "proof" in message:
        return (
            "When voting or registering, you generally need valid identification:\n"
            "1. Photo ID: A driver's license, passport, or state/national ID card.\n"
            "2. Proof of Address: A recent utility bill or bank statement.\n"
            "3. Voter ID Card: Issued by your local election commission (if applicable).\n"
            "Always verify exact requirements on your local election website!"
        )
    elif "where to vote" in message or "polling booth" in message or "location" in message:
        return (
            "To find your polling booth or voting location:\n"
            "1. Visit your state or national election commission website.\n"
            "2. Look for the 'Find My Polling Station' or 'Voter Search' tool.\n"
            "3. Enter your Voter ID number or personal details to find the exact address.\n"
            "4. Make sure to double-check the location a few days before Election Day!"
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
    else:
        return (
            "I can help with:\n"
            "• How to vote\n"
            "• Voter registration\n"
            "• Documents required\n"
            "• Where to vote\n"
            "• EVM & NOTA\n\n"
            "Try asking one of these!"
        )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "Message is required"}), 400
        
    bot_response = get_bot_response(user_message)
    
    # Store in Firebase if initialized
    if firebase_initialized and db:
        try:
            doc_ref = db.collection("chat_queries").document()
            doc_ref.set({
                "user_query": user_message,
                "bot_response": bot_response,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            print("Data stored successfully")
        except Exception as e:
            print(f"Failed to write to Firebase: {e}")
            
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
