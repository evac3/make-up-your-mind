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
    assert profile.json() == {
        "id": created["user_id"],
        **PROFILE,
        "email": None,
        "phone_number": None,
        "traits": [],
    }


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
    assert set(decision) == {"id", "message", "ai_response", "outcome", "timestamp", "conversation_id"}
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


def test_auth_signup_and_login_flow(client):
    signup_payload = {
        "name": "Alex",
        "email": "alex@example.com",
        "phone_number": "+1234567890",
        "password": "secretpassword123",
        "condition": "anxiety",
        "about_me": "College student facing big career decisions",
        "concerns": "Overthinking and catastrophizing",
        "traits": ["overthinker", "student", "perfectionist"],
    }
    signup_resp = client.post("/auth/signup", json=signup_payload)
    assert signup_resp.status_code == 201, signup_resp.text
    user_id = signup_resp.json()["user_id"]
    assert isinstance(user_id, int)

    dup_email_resp = client.post("/auth/signup", json={
        **signup_payload,
        "phone_number": "+1999999999",
    })
    assert dup_email_resp.status_code == 409

    dup_phone_resp = client.post("/auth/signup", json={
        **signup_payload,
        "email": "different@example.com",
    })
    assert dup_phone_resp.status_code == 409

    login_email_resp = client.post("/auth/login", json={
        "email": "alex@example.com",
        "password": "secretpassword123",
    })
    assert login_email_resp.status_code == 200
    assert login_email_resp.json()["user_id"] == user_id
    assert login_email_resp.json()["name"] == "Alex"

    login_phone_resp = client.post("/auth/login", json={
        "phone_number": "+1234567890",
        "password": "secretpassword123",
    })
    assert login_phone_resp.status_code == 200
    assert login_phone_resp.json()["user_id"] == user_id

    wrong_pwd_resp = client.post("/auth/login", json={
        "email": "alex@example.com",
        "password": "wrongpassword",
    })
    assert wrong_pwd_resp.status_code == 401


def test_user_profile_edit_rules(client):
    signup_resp = client.post("/auth/signup", json={
        "name": "Jordan",
        "email": "jordan@example.com",
        "phone_number": "+15551234567",
        "password": "mypassword1",
        "traits": ["night owl"],
    })
    user_id = signup_resp.json()["user_id"]

    profile = client.get(f"/user/{user_id}").json()
    assert profile["name"] == "Jordan"
    assert profile["email"] == "jordan@example.com"
    assert profile["phone_number"] == "+15551234567"
    assert profile["traits"] == ["night owl"]

    patch_resp = client.patch(f"/user/{user_id}", json={
        "name": "Jordan Smith",
        "traits": ["night owl", "mindful", "working on focus"],
        "password": "newpassword456",
    })
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["name"] == "Jordan Smith"
    assert updated["traits"] == ["night owl", "mindful", "working on focus"]
    assert updated["email"] == "jordan@example.com"
    assert updated["phone_number"] == "+15551234567"

    login_resp = client.post("/auth/login", json={
        "email": "jordan@example.com",
        "password": "newpassword456",
    })
    assert login_resp.status_code == 200


def test_user_settings_toggles(client):
    signup_resp = client.post("/auth/signup", json={
        "name": "Sam",
        "email": "sam@example.com",
        "phone_number": "+18881234567",
        "password": "password123",
    })
    user_id = signup_resp.json()["user_id"]

    settings = client.get(f"/settings/{user_id}").json()
    assert settings["appearance"] == "light"
    assert settings["notifications_email"] is True
    assert settings["accessibility_large_text"] is False
    assert settings["privacy_save_chats"] is True

    update_resp = client.put(f"/settings/{user_id}", json={
        "appearance": "dark",
        "notifications_email": False,
        "accessibility_large_text": True,
        "accessibility_tts": True,
        "privacy_save_chats": False,
    })
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["appearance"] == "dark"
    assert updated["notifications_email"] is False
    assert updated["accessibility_large_text"] is True
    assert updated["accessibility_tts"] is True
    assert updated["privacy_save_chats"] is False


def test_conversations_with_ai_topic_and_follow_ups(client):
    signup_resp = client.post("/auth/signup", json={
        "name": "Taylor",
        "email": "taylor@example.com",
        "phone_number": "+17771234567",
        "password": "password123",
    })
    user_id = signup_resp.json()["user_id"]

    conv_resp = client.post("/conversation", json={
        "user_id": user_id,
        "topic": "Dropping Physics 101",
        "message": "Should I drop physics 101 to protect my mental health?",
        "ai_response": "Let's break this down into short and long term consequences...",
    })
    assert conv_resp.status_code == 200, conv_resp.text
    conv = conv_resp.json()
    conv_id = conv["id"]
    assert conv["topic"] == "Dropping Physics 101"
    assert len(conv["messages"]) == 1
    first_msg_id = conv["messages"][0]["id"]
    assert conv["messages"][0]["message"] == "Should I drop physics 101 to protect my mental health?"

    msg_resp = client.post(f"/conversation/{conv_id}/message", json={
        "user_id": user_id,
        "message": "What if it delays my graduation by a semester?",
        "ai_response": "Graduating one semester later is far less impactful than burnout...",
    })
    assert msg_resp.status_code == 200
    second_decision = msg_resp.json()
    assert second_decision["conversation_id"] == conv_id

    list_resp = client.get(f"/conversations/{user_id}")
    assert list_resp.status_code == 200
    conversations = list_resp.json()
    assert len(conversations) == 1
    assert conversations[0]["topic"] == "Dropping Physics 101"
    assert conversations[0]["message_count"] == 2

    detail_resp = client.get(f"/conversation/{conv_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["messages"]) == 2
    assert detail["messages"][0]["message"] == "Should I drop physics 101 to protect my mental health?"
    assert detail["messages"][1]["message"] == "What if it delays my graduation by a semester?"

    outcome_resp = client.post("/outcome", json={
        "decision_id": first_msg_id,
        "outcome": "I dropped the class and felt an immediate weight lifted. Ended up making Dean's list.",
    })
    assert outcome_resp.status_code == 200

    recheck_resp = client.get(f"/conversation/{conv_id}")
    assert recheck_resp.json()["messages"][0]["outcome"] == (
        "I dropped the class and felt an immediate weight lifted. Ended up making Dean's list."
    )

