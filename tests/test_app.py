import pytest


PROFILE = {
    "name": "John",
    "condition": "I have anxiety and struggle with big decisions",
    "about_me": "I'm a college student dealing with a lot of stress",
    "concerns": "I worry about making the wrong choice and regretting it",
}


def create_user(client, **overrides):
    payload = {**PROFILE, **overrides}
    response = client.post("/user", json=payload)
    assert response.status_code == 200, response.text
    return response.json()["user_id"]


def test_health_endpoints(client):
    assert client.get("/").json() == {"app": "make-up-your-mind", "status": "running"}
    assert client.get("/health").json() == {"status": "ok"}


def test_user_profile_contract(client):
    response = client.post("/user", json=PROFILE)
    assert response.status_code == 200, response.text
    created = response.json()
    assert created == {
        "user_id": created["user_id"],
        "message": "Profile created successfully",
    }
    assert isinstance(created["user_id"], int)

    profile = client.get(f"/user/{created['user_id']}")
    assert profile.status_code == 200, profile.text
    assert profile.json() == {"id": created["user_id"], **PROFILE}


def test_decision_history_and_outcome_contract(client):
    user_id = create_user(client)
    decision_response = client.post(
        "/decision",
        json={
            "user_id": user_id,
            "message": "Should I drop this class?",
            "ai_response": "Let's think through this together...",
        },
    )
    assert decision_response.status_code == 200, decision_response.text
    decision = decision_response.json()
    assert set(decision) == {"id", "message", "ai_response", "outcome", "timestamp"}
    assert decision["message"] == "Should I drop this class?"
    assert decision["ai_response"] == "Let's think through this together..."
    assert decision["outcome"] is None

    history_response = client.get(f"/history/{user_id}")
    assert history_response.status_code == 200, history_response.text
    assert history_response.json() == {"decisions": [decision]}

    outcome_response = client.post(
        "/outcome",
        json={"decision_id": decision["id"], "outcome": "I stayed and passed the class"},
    )
    assert outcome_response.status_code == 200, outcome_response.text
    assert outcome_response.json() == {
        "decision_id": decision["id"],
        "outcome": "I stayed and passed the class",
        "message": "Outcome updated successfully",
    }
    updated = client.get(f"/history/{user_id}").json()["decisions"][0]
    assert updated["outcome"] == "I stayed and passed the class"


def test_history_is_scoped_and_newest_first(client):
    first_user = create_user(client)
    second_user = create_user(client, name="Mary")
    ids = []
    for user_id, message in [
        (first_user, "First question"),
        (second_user, "Other user's question"),
        (first_user, "Latest question"),
    ]:
        response = client.post(
            "/decision",
            json={"user_id": user_id, "message": message, "ai_response": "AI response"},
        )
        assert response.status_code == 200
        ids.append(response.json()["id"])

    first_history = client.get(f"/history/{first_user}").json()["decisions"]
    second_history = client.get(f"/history/{second_user}").json()["decisions"]
    assert [item["id"] for item in first_history] == [ids[2], ids[0]]
    assert [item["id"] for item in second_history] == [ids[1]]


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("GET", "/user/999", None),
        ("GET", "/history/999", None),
        (
            "POST",
            "/decision",
            {"user_id": 999, "message": "Question", "ai_response": "Response"},
        ),
        ("POST", "/outcome", {"decision_id": 999, "outcome": "Good"}),
    ],
)
def test_missing_records_return_404(client, method, path, payload):
    response = client.request(method, path, **({"json": payload} if payload else {}))
    assert response.status_code == 404


@pytest.mark.parametrize("field", ["name", "condition", "about_me", "concerns"])
def test_user_profile_fields_are_required(client, field):
    payload = PROFILE.copy()
    payload.pop(field)
    assert client.post("/user", json=payload).status_code == 422


def test_cors_allows_react_development_origin(client):
    response = client.options(
        "/user",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
