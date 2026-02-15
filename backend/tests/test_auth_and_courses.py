def test_signup_and_login(client):
    signup_payload = {
        "full_name": "Student One",
        "email": "student1@example.com",
        "phone": "7000000001",
        "grade_or_standard": "8",
        "password": "Password@123",
    }
    r = client.post("/auth/signup", json=signup_payload)
    assert r.status_code == 200
    assert r.json()["role"] == "student"

    login = client.post("/auth/login", json={"email": signup_payload["email"], "password": signup_payload["password"]})
    assert login.status_code == 200
    data = login.json()
    assert data["access_token"]
    assert data["refresh_token"]


def test_student_course_listing(client):
    signup_payload = {
        "full_name": "Student Two",
        "email": "student2@example.com",
        "phone": "7000000002",
        "grade_or_standard": "9",
        "password": "Password@123",
    }
    client.post("/auth/signup", json=signup_payload)
    login = client.post("/auth/login", json={"email": signup_payload["email"], "password": signup_payload["password"]})
    token = login.json()["access_token"]

    courses = client.get("/courses", headers={"Authorization": f"Bearer {token}"})
    assert courses.status_code == 200
    assert isinstance(courses.json(), list)
