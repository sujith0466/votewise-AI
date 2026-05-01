"""
test_app.py — Lightweight unit tests for VoteWise AI.
Uses Flask's built-in test client. No external test dependencies required.
Run with: python -m pytest test_app.py -v  (or simply: python test_app.py)
"""
import sys
import os

# Ensure the app module is importable
sys.path.insert(0, os.path.dirname(__file__))

from app import app, get_rule_based_response


def get_client():
    """Create a Flask test client."""
    app.config["TESTING"] = True
    return app.test_client()


# ─── Rule-Based Response Tests ───

def test_rule_how_to_vote():
    result = get_rule_based_response("how to vote")
    assert result is not None
    assert "polling station" in result.lower()

def test_rule_first_time_voter():
    result = get_rule_based_response("I am a first time voter")
    assert result is not None
    assert "eligibility" in result.lower() or "register" in result.lower()

def test_rule_evm():
    result = get_rule_based_response("What is EVM?")
    assert result is not None
    assert "electronic voting machine" in result.lower()

def test_rule_nota():
    result = get_rule_based_response("What is NOTA?")
    assert result is not None
    assert "none of the above" in result.lower()

def test_rule_no_match_returns_none():
    result = get_rule_based_response("What is the weather today?")
    assert result is None


# ─── Input Validation Tests ───

def test_empty_input_returns_400():
    client = get_client()
    r = client.post("/api/chat", json={"message": "", "language": "en"})
    assert r.status_code == 400
    data = r.get_json()
    assert data["status"] == "error"

def test_long_input_returns_400():
    client = get_client()
    r = client.post("/api/chat", json={"message": "a" * 501, "language": "en"})
    assert r.status_code == 400
    data = r.get_json()
    assert data["status"] == "error"

def test_missing_body_returns_400():
    client = get_client()
    r = client.post("/api/chat", data="not json", content_type="text/plain")
    assert r.status_code == 400


# ─── API Behavior Tests ───

def test_chat_success_rule_based():
    client = get_client()
    r = client.post("/api/chat", json={"message": "how to vote", "language": "en"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "success"
    assert len(data["response"]) > 0

def test_homepage_loads():
    client = get_client()
    r = client.get("/")
    assert r.status_code == 200

def test_response_json_structure():
    client = get_client()
    r = client.post("/api/chat", json={"message": "evm", "language": "en"})
    data = r.get_json()
    assert "response" in data
    assert "status" in data


# ─── Routing Priority Test ───

def test_rule_based_takes_priority_over_gemini():
    """Rule-based engine must respond to known keywords without invoking Gemini."""
    # These queries all have rule matches — response must be instant and deterministic
    rule_triggers = ["how to vote", "register", "evm", "nota", "first time voter"]
    for query in rule_triggers:
        result = get_rule_based_response(query)
        assert result is not None, f"Expected rule-based match for: '{query}', got None"


# ─── Additional Edge Case Tests ───

def test_rule_register():
    """'register' keyword must match the voter registration rule."""
    result = get_rule_based_response("How do I register to vote?")
    assert result is not None
    assert "form" in result.lower() or "register" in result.lower()

def test_rule_polling_booth():
    """'polling booth' keyword must match the polling location rule."""
    result = get_rule_based_response("Where is my polling booth?")
    assert result is not None
    assert "election commission" in result.lower() or "polling" in result.lower()

def test_rule_age_eligible():
    """Age >= 18 must return an eligibility confirmation."""
    result = get_rule_based_response("I am 22 years old from Delhi")
    assert result is not None
    assert "eligible" in result.lower()

def test_rule_age_ineligible():
    """Age < 18 must return a 'must wait' response."""
    result = get_rule_based_response("I am 16 years old")
    assert result is not None
    assert "18" in result


# ─── Mock & Header Tests ───

def test_x_request_id_header_present():
    """Every API response must include a unique X-Request-ID header."""
    client = get_client()
    r = client.post("/api/chat", json={"message": "how to vote", "language": "en"})
    assert "X-Request-ID" in r.headers
    assert len(r.headers["X-Request-ID"]) == 36  # UUID4 format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

def test_gemini_fallback_on_offline(monkeypatch):
    """When Gemini is offline, get_gemini_response must return a safe fallback string."""
    import app as app_module
    # Force the initialized flag to False so the offline guard triggers
    monkeypatch.setattr(app_module, "gemini_initialized", False)
    result = app_module.get_gemini_response("explain democracy")
    assert result is not None
    assert len(result) > 0  # Non-empty fallback message returned
    assert "how to vote" in result.lower() or "try asking" in result.lower() or "documents" in result.lower()

def test_security_headers_present():
    """All required security headers must be present on every API response."""
    client = get_client()
    r = client.post("/api/chat", json={"message": "how to vote", "language": "en"})
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert "Content-Security-Policy" in r.headers
    assert "X-Request-ID" in r.headers

def test_invalid_language_falls_back_to_english():
    """Unsupported language codes must be silently normalised to 'en'."""
    client = get_client()
    r = client.post("/api/chat", json={"message": "how to vote", "language": "fr"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "success"
    assert len(data["response"]) > 0



# ─── Run directly ───

if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR {test.__name__}: {e}")
            failed += 1
    print(f"\nResults: {passed} passed, {failed} failed out of {passed + failed}")
    sys.exit(1 if failed else 0)
