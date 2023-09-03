"""
Test for Tag APIs.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Tag

TAGS_URL = reverse('recipe:tag-list')


def create_dummy_user(email='usertag@example.com', password='thisispassowrd'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


class PublicTagsApiTest(TestCase):
    """Tes un-authenticate API request."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required to call Tag API."""
        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatgeTagsApiTest(TestCase):
    """Test authenticated API request."""

    def setUp(self):
        # setUp before test class started
        self.user = create_dummy_user()

        # authenticate using create user
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_recipes(self):
        """Test retrive a list of recipes."""

        Tag.objects.create(self.user, "Vegan")
        Tag.objects.create(self.user, "Dessert")
        Tag.objects.create(user=self.user, name="Herbal")

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = create_dummy_user(
            email='othe@example.com',
            password='testpass123',
        )

        Tag.objects.create(user=other_user, name="Herbal other")
        tag_created_by_user = Tag.objects.create(self.user, "Vegan")

        response = self.client.get(TAGS_URL)

        # recipes = TAGS_URL.objects.filter(user=self.user).order_by('-id')
        # serializer = TagSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]['name'], tag_created_by_user.name)
        self.assertEqual(response.data[0]['id'], tag_created_by_user.id)
