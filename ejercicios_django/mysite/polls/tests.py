from django.contrib.auth.models import User
from django.test import TestCase


class UserTests(TestCase):
    def setUp(self):
        User.objects.create_user("test", "admin@gmail.com", "prueba123")

    def test_user_logeado(self):
        logeado = User.objects.filter(user__name="test").exists()
        self.assertEqual(logeado, True)
