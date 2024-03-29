import requests
import unittest

from tests.test_helpers import create_test_user, clear_posts

class TestPostApis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.host = 'http://127.0.0.1:8080'
        cls.username, cls.password = create_test_user()

    def setUp(self):
        clear_posts()

    def test_post_apis(self):
        with requests.Session() as session:
            # Post a cat pic but not logged in
            response = session.post(f'{self.host}/post/create', data={"title": "test title", "description": "test description"}, files={'file': open('tests/imgs/test_cat1.jpeg', 'rb')})
            assert response.status_code == 401
            # Post a non-cat pic but not logged in
            response = session.post(f'{self.host}/post/create', data={"title": "test title", "description": "test description"}, files={'file': open('tests/imgs/test_not_cat.jpeg', 'rb')})
            assert response.status_code == 401
            # Login
            response = session.post(f'{self.host}/users/login', json={"username": self.username, "password": self.password})
            assert response.status_code == 200
            # Post a cat pic
            response = session.post(f'{self.host}/post/create', data={"title": "test title", "description": "test description"}, files={'file': open('tests/imgs/test_cat1.jpeg', 'rb')})
            assert response.status_code == 200
            # Try to post a non-cat pic
            response = session.post(f'{self.host}/post/create', data={"title": "test title", "description": "test description"}, files={'file': open('tests/imgs/test_not_cat.jpeg', 'rb')})
            assert response.status_code == 418
            # Post a different cat pic
            response = session.post(f'{self.host}/post/create', data={"title": "test title", "description": "test description"}, files={'file': open('tests/imgs/test_cat2.jpeg', 'rb')})
            assert response.status_code == 200
            # Get all posts made by the test user
            response = session.get(f'{self.host}/posts/user/{self.username}')
            assert response.status_code == 200
            get_user_posts_response_json = response.json()
            assert len(get_user_posts_response_json) == 2 # We tried to post 2 cats and 1 non cat so there should be 2 posts
            # Get the image for each post
            for i in range(len(get_user_posts_response_json)):
                response = session.get(f'{self.host}/post/image/{get_user_posts_response_json[i]["image_name"]}')
                assert response.status_code == 200
                response = session.get(f'{self.host}/post/image/{get_user_posts_response_json[i]["image_name"]}')
                assert response.status_code == 200
            # Test quality parameter image compression
            response_low = session.get(f'{self.host}/post/image/{get_user_posts_response_json[i]["image_name"]}/?quality=low')
            response_mid = session.get(f'{self.host}/post/image/{get_user_posts_response_json[i]["image_name"]}/?quality=mid')
            assert len(response_low.content) < len(response_mid.content)
            response_high = session.get(f'{self.host}/post/image/{get_user_posts_response_json[i]["image_name"]}/?quality=high')
            assert len(response_mid.content) < len(response_high.content)
            # Get a random post
            response = session.get(f'{self.host}/post/random')
            assert response.status_code == 200
            response_json = response.json()
            assert "title" in response_json.keys()
            assert "description" in response_json.keys()
            assert "image_name" in response_json.keys()
            assert "poster_username" in response_json.keys()
            # Like the random post
            response = session.post(f'{self.host}/post/like/{response_json["post_id"]}')
            assert response.status_code == 200
            # Liking the same post by same user should result in code 409
            response = session.post(f'{self.host}/post/like/{response_json["post_id"]}')
            assert response.status_code == 409
            # Get the number of likes on this post noq
            response = session.get(f'{self.host}/post/likes/{response_json["post_id"]}')
            assert response.status_code == 200
            assert response.json() == 1
        # make a second user session
        with requests.Session() as session:
            # A non-logged in user shouldnt be allowed to like posts
            response = session.post(f'{self.host}/post/like/{response_json["post_id"]}')
            assert response.status_code == 401