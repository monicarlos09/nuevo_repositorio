import datetime
from django.contrib.auth.decorators import user_passes_test

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from django.contrib.auth.models import User

from .models import Question


class UserTests(TestCase):
    def setUp(self):
        usuario = User.objects.create_user(
            'test', 'admin@gmail.com', 'prueba123')

    def test_user_logeado(self):
        logeado = User.objects.filter(user__name='test').exists()
        self.assertEqual(logeado, True)
