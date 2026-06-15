import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

# This fixture automatically provides a fresh, logged-in token to any test that requests it
@pytest.fixture
def auth_token():
    username = f"test_{uuid.uuid4().hex[:8]}"
    password = "password123"
    requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    resp = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    return resp.json().get("token")

# --- CUSTOM REPORT GENERATOR ---
def pytest_sessionstart(session):
    """Creates a fresh report file when the test suite begins."""
    with open("test_report.md", "w", encoding="utf-8") as f:
        f.write("# API Interface Test Report\n\n")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Intercepts each test result and writes its docstring and status to the report."""
    outcome = yield
    rep = outcome.get_result()
    
    # We only care about the actual execution phase ('call'), not setup/teardown
    if rep.when == "call":
        with open("test_report.md", "a", encoding="utf-8") as f:
            status = "✅ PASSED" if rep.passed else f"❌ FAILED\n**Error:** {rep.longreprtext.splitlines()[-1]}"
            # Extract the docstring we write in the tests to explain what we are checking
            doc = item.function.__doc__ or "No description provided."
            # Clean up docstring formatting
            doc = " ".join([line.strip() for line in doc.split("\n") if line.strip()])
            
            f.write(f"### Test: `{item.name}`\n")
            f.write(f"**Result:** {status}\n")
            f.write(f"**What this checked:** {doc}\n\n")
            f.write("---\n\n")