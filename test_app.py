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
