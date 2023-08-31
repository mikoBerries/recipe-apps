"""
Test for  modles.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    """ Test models"""

    def text_create_user_with_email_successful(self):
        """Test creating uset with an email"""

        email = "test@example.com"
        password = "Test1234"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        # checking model
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
