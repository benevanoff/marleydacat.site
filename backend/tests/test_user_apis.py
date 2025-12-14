import requests
import unittest

from scripts.create_invite_token import createAndAddInviteToken

class TestUserApis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.host = 'http://127.0.0.1:8080'

    def test_user_apis(self):
        test_username = "test"
        test_password = "password"

        with requests.Session() as session:
            # Try to login with no users currently exist in database
            response = session.post(f'{self.host}/users/login', json={"username": "njo238hrn23i4br", "password": "password"})
            assert response.status_code == 401
            # Try to register a user with an invalid token
            response = session.post(f'{self.host}/users/register', json={"username": test_username, "password": test_password, "email": "test@test.com", "invite_token": "abc123"})
            assert response.status_code == 403
            # Register a fresh user
            fresh_token = createAndAddInviteToken()
            response = session.post(f'{self.host}/users/register', json={"username": test_username, "password": test_password, "email": "test@test.com", "invite_token": fresh_token})
            assert response.status_code == 200
            # Non existant user id -> unauthorized
            response = session.post(f'{self.host}/users/login', json={"username": "njo238hrn23i4br", "password": "password"})
            assert response.status_code == 401
            # Wrong password -> unauthorized
            response = session.post(f'{self.host}/users/login', json={"username": test_username, "password": "badpassword"})
            assert response.status_code == 401
            # Correct username/password pair -> authorized and set cookie
            response = session.post(f'{self.host}/users/login', json={"username": test_username, "password": test_password})
            assert response.status_code == 200
            assert response.cookies.get("session_id") is not None
            # Whoami endpoint should say this session belongs to the test user
            response = session.get(f'{self.host}/users/whoami')
            assert response.status_code == 200
            response_json = response.json()
            assert response_json["username"] == "test"
            # Now logout
            response = session.post(f'{self.host}/users/logout')
            assert response.status_code == 200
            # Now whoami should return None
            response = session.get(f'{self.host}/users/whoami')
            assert response.status_code == 200
            assert response.json() is None
