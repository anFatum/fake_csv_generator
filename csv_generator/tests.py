from django.test import TestCase
from django.contrib.auth import get_user_model, get_user
from django.shortcuts import reverse
from django.test.client import Client
from csv_generator.models import Schema, Character
from csv_generator.models.choices import CharacterType

User = get_user_model()


class BasicViewTests(TestCase):
    def testGetIndexNoLogin(self):
        response = self.client.get(reverse("csv:index"))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertTrue("/auth/login" in response.url)


class SchemaViewTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user("test", password="test_1234")
        columns_sep = Character.objects.create(character="d",
                                               character_type=CharacterType.COLUMN_SEPARATOR)
        string_char = Character.objects.create(character="f",
                                               character_type=CharacterType.STRING_CHARACTER)
        self.user_schema = Schema.objects.create(title="Title_1",
                                                 owner=self.user,
                                                 column_separator=columns_sep,
                                                 string_character=string_char)
        self.client = Client()

    def testGetIndex(self):
        self.client.login(username="test", password="test_1234")
        response = self.client.get(reverse("csv:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user_schema.title.encode() in response.content)
