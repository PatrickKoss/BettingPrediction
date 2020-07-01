from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.test import RequestsClient


class TestLogin(APITestCase):
    def setUp(self):
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client = RequestsClient()
        self.maxDiff = None

    def test_empty(self):
        response = self.client.post('http://127.0.0.1:8000/user/login/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_authentication(self):
        response = self.client.post('http://127.0.0.1:8000/user/login/',
                                    json={"username": "wrong", "password": "wrongPW"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid(self):
        response = self.client.post('http://127.0.0.1:8000/user/login/',
                                    json={"username": "User1", "password": "secretPW"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestLogout(APITestCase):
    def setUp(self):
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client = RequestsClient()
        self.maxDiff = None

    def test_logout(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post('http://127.0.0.1:8000/user/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestGetAuthenticated(APITestCase):
    def setUp(self):
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client = RequestsClient()
        self.maxDiff = None

    def test_no_authentication_sent(self):
        response = self.client.get('http://127.0.0.1:8000/user/authenticated/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_authentication_sent(self):
        self.client.headers.update({"Authorization": "asdf"})
        response = self.client.get('http://127.0.0.1:8000/user/authenticated/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_correct_authentication(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.get('http://127.0.0.1:8000/user/authenticated/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestRegister(APITestCase):
    def setUp(self):
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        if not User.objects.filter(username='User2').exists():
            self.normal_user = User.objects.create_user(username="User2", password="secretPW", email="user2@gmail.com")
            self.normal_user_token, _ = Token.objects.get_or_create(user=self.normal_user)
        self.client = RequestsClient()
        self.maxDiff = None

    def test_no_permission(self):
        self.client.headers.update({"Authorization": self.normal_user_token.key})
        response = self.client.post('http://127.0.0.1:8000/user/register/',
                                    json={"username": "User3", "password": "secretPW", "email": "user3@gmail.com"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_valid(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post('http://127.0.0.1:8000/user/register/',
                                    json={"username": "User3", "password": "secretPW", "email": "user3@gmail.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestDeleteUser(APITestCase):
    def setUp(self):
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        if not User.objects.filter(username='User2').exists():
            self.normal_user = User.objects.create_user(username="User2", password="secretPW", email="user2@gmail.com")
            self.normal_user_token, _ = Token.objects.get_or_create(user=self.normal_user)
        if not User.objects.filter(username='User3').exists():
            self.delete_user = User.objects.create_user(username="User3", password="secretPW", email="user3@gmail.com")
            self.delete_user_token, _ = Token.objects.get_or_create(user=self.delete_user)
        self.client = RequestsClient()
        self.maxDiff = None

    def test_no_permission(self):
        self.client.headers.update({"Authorization": self.normal_user_token.key})
        response = self.client.delete(f'http://127.0.0.1:8000/user/delete/{self.delete_user.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_valid(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.delete(f'http://127.0.0.1:8000/user/delete/{self.delete_user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_user_to_delete(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.delete(f'http://127.0.0.1:8000/user/delete/100')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUpdateUser(APITestCase):
    def setUp(self):
        if not User.objects.filter(username='User1').exists():
            self.admin = User.objects.create_superuser(username="User1", password="secretPW", email="user1@gmail.com")
            self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        if not User.objects.filter(username='User2').exists():
            self.normal_user = User.objects.create_user(username="User2", password="secretPW", email="user2@gmail.com")
            self.normal_user_token, _ = Token.objects.get_or_create(user=self.normal_user)
        self.client = RequestsClient()
        self.maxDiff = None

    def test_valid(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/user/update/',
                                    json={"username": "Admin", "password": "password", "email": "email@gmail.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_data_sent(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/user/update/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_one_attribute_not_sent(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/user/update/',
                                    json={"username": "Admin", "password": "password"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_already_exist(self):
        self.client.headers.update({"Authorization": self.admin_token.key})
        response = self.client.post(f'http://127.0.0.1:8000/user/update/',
                                    json={"username": "User2", "password": "password", "email": "email@gmail.com"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
