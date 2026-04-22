import os
import json
import datetime
from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

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
    
    # Age/Eligibility detection
    if ("i am" in message or "i'm" in message or "age is" in message) and any(char.isdigit() for char in message):
        import re
        numbers = re.findall(r'\d+', message)
        if numbers:
            age = int(numbers[0])
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
            "When voting or registering, you generally need valid identification:\n"
            "1. Photo ID: A driver's license, passport, or state/national ID card.\n"
            "2. Proof of Address: A recent utility bill or bank statement.\n"
            "3. Voter ID Card: Issued by your local election commission (if applicable).\n"
            "Always verify exact requirements on your local election website!"
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
    else:
        return (
            "Try asking:\n"
            "• How to vote\n"
            "• Documents required\n"
            "• First-time voter guide\n"
            "• Where to vote"
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
