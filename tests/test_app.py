"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns status code 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_fields(self):
        """Test that activities contain expected fields"""
        response = client.get("/activities")
        activities = response.json()
        
        # Check that at least one activity exists
        assert len(activities) > 0
        
        # Check that each activity has required fields
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@example.com"
        )
        assert response.status_code == 200
        assert "message" in response.json()

    def test_signup_adds_participant(self):
        """Test that signup adds participant to the activity"""
        email = "newstudent@mergington.edu"
        
        # Get initial participants count
        initial = client.get("/activities").json()
        initial_count = len(initial["Programming Class"]["participants"])
        
        # Sign up
        response = client.post(
            "/activities/Programming Class/signup?email=" + email
        )
        assert response.status_code == 200
        
        # Check that participant was added
        updated = client.get("/activities").json()
        updated_count = len(updated["Programming Class"]["participants"])
        assert updated_count == initial_count + 1
        assert email in updated["Programming Class"]["participants"]

    def test_signup_twice_fails(self):
        """Test that signing up twice for the same activity fails"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Drama Club/signup?email=" + email
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Drama Club/signup?email=" + email
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_for_nonexistent_activity_fails(self):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Fake Activity/signup?email=test@example.com"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        email = "unregister@mergington.edu"
        
        # First, sign up
        client.post("/activities/Art Studio/signup?email=" + email)
        
        # Then unregister
        response = client.delete(
            "/activities/Art Studio/unregister?email=" + email
        )
        assert response.status_code == 200
        assert "message" in response.json()

    def test_unregister_removes_participant(self):
        """Test that unregister removes participant from the activity"""
        email = "remove@mergington.edu"
        
        # Sign up
        client.post("/activities/Science Club/signup?email=" + email)
        
        # Check participant is there
        activities = client.get("/activities").json()
        assert email in activities["Science Club"]["participants"]
        
        # Unregister
        client.delete("/activities/Science Club/unregister?email=" + email)
        
        # Check participant is removed
        activities = client.get("/activities").json()
        assert email not in activities["Science Club"]["participants"]

    def test_unregister_nonexistent_activity_fails(self):
        """Test that unregistering from a non-existent activity fails"""
        response = client.delete(
            "/activities/Fake Activity/unregister?email=test@example.com"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_nonparticipant_fails(self):
        """Test that unregistering someone not signed up fails"""
        response = client.delete(
            "/activities/Tennis Club/unregister?email=notregistered@example.com"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
