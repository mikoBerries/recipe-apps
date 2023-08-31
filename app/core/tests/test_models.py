"""
Test for  modles.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    """ Test models"""

    def test_create_user_with_email_successful(self):
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

    def test_new_create_user_email_normalized(self):
        """Temp email is normalized for new users."""

        # sample test case and result
        sample_email = [
            ['test1@eXamPle.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.CoM', 'test4@example.com']
        ]

        # Loop all test case
        for email, expected in sample_email:
            user = get_user_model().objects.create_user(email)
            self.assertEquals(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating user without an email will raises valueerror"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('')

    def test_create_superuser(self):
        """"TEst creating a super user."""
        user = get_user_model().objects.create_superuser(
            'test@exmaple.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)