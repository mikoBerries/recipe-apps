"""
Tests for user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test Creating a user (Returning success)"""

        payload = {
            'email': 'text@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        # POST to django API
        response = self.client.post(create_user, payload)

        # Check response
        # check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # get user from DB
        created_user = get_user_model().objects.get(email=payload['email'])

        self.assertEqual(create_user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_with_email_exist_error(self):
        """Test error returnd if user with same email exists in app."""
        payload = {
            'email': 'text@example.com',
            'password': 'testpass123',
            'name': 'Test name'
        }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)

        # check response is bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        def test_password_too_short_error(self):
            """Test an error is returned if passowd less than settings"""
        payload = {
            'email': 'text@example.com',
            'password': 'pas',
            'name': 'Test name'
        }
        response = self.client.post(CREATE_USER_URL, payload)

        # check response
        # response status_code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # check user in database exists?
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generate token for valid credentials"""

        # Create user
        user_details = {
            'name': 'TestName',
            'email': 'text@example.com',
            'password': 'testpassword',
        }

        create_user(**user_details)

        # create token
        payload = {
            'email': user_details['name'],
            'password': user_details['password'],
        }
        response = self.client.post(TOKEN_URL, payload)

        # Check response
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns a error if credentials invalid."""

        # Create user
        user_details = {
            'name': 'TestName',
            'email': 'text@example.com',
            'password': 'testpassword',
        }

        create_user(**user_details)

        # create token
        payload = {
            'email': 'TestName',
            'password': 'tampperedpassword',
        }

        response = self.client.post(TOKEN_URL, payload)

        # Check response
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank passowrd return an error"""
        # create token
        payload = {
            'email': 'Test name',
            'password': '',
        }

        response = self.client.post(TOKEN_URL, payload)
        # Check response
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
