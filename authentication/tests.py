from django.test import TestCase
from django.contrib.auth import get_user_model, get_user
from authentication.forms import LoginForm
from django.shortcuts import reverse
from django.test.client import Client

User = get_user_model()


class TestLoginForm(TestCase):
    def test_form_valid(self):
        user = User.objects.create_user("test", password="test_1234")
        data = {'username': user.username, 'password': "test_1234"}
        form = LoginForm(data=data)
        self.assertTrue(form.is_valid(), "Form should be valid")

    def test_form_invalid(self):
        user = User.objects.create_user("test", password="test_1234")
        data = {'username': user.username, 'password': ""}
        form = LoginForm(data=data)
        self.assertFalse(form.is_valid(), "Form should be invalid")


class TestLoginViews(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create_user("test", password="test_1234")

    def testLoginView(self):
        response = self.client.get(reverse("authentication:login"))
        self.assertEqual(response.status_code, 200)

    def testLoginUser(self):
        response = self.client.post(reverse("authentication:login"),
                                    data={
                                        'username': self.user.username,
                                        'password': "test_1234"
                                    })
        user = get_user(self.client)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url == '/')
        self.assertTrue(user.is_authenticated)

    def testLoginWrongCredentialsUser(self):
        response = self.client.post(reverse("authentication:login"),
                                    data={
                                        'username': self.user.username,
                                        'password': "te_1234"
                                    })
        user = get_user(self.client)
        self.assertTrue("Wrong credentials", response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.status_code, 302)
        self.assertFalse(user.is_authenticated)

    def testLogoutNoLoggedIn(self):
        response = self.client.get(reverse("authentication:logout"))
        user = get_user(self.client)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url == '/')
        self.assertFalse(user.is_authenticated)

    def testLogoutLoggedIn(self):
        self.client.login(username=self.user.username,
                          pasword="test_1234")
        response = self.client.get(reverse("authentication:logout"))
        user = get_user(self.client)
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url == '/')
        self.assertFalse(user.is_authenticated)
