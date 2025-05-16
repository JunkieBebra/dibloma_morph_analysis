from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Text, Dictionary, DictionaryEntry, Word

class APITestSetup(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.text = Text.objects.create(title='Test', author='Author', user=self.user)
        self.dictionary = Dictionary.objects.create(title='Dict', user=self.user)
        self.word = Word.objects.create(value='hello')
        self.entry = DictionaryEntry.objects.create(dictionary=self.dictionary, word=self.word)


