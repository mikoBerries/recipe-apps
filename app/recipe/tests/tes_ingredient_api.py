"""
Test for the ingredients API.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializer import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def create_dummy_user(email='user_ingredients_api@example.com', password='thisispassowrd'):
    """Create and return a new user for testing."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientTest(TestCase):
    """Test un-authenticated API request."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required fore retiving ingredient"""

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientTest(TestCase):
    """Test authenticated API request."""

    def setUp(self):
        self.user = create_dummy_user()

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""

        Ingredient.objects.create(user=self.user, name='cola')
        Ingredient.objects.create(user=self.user, name='bake')

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(response.data, serializer.data)

    def test_retrieve_ingredients_limited_to_user(self):
        """Test list of ingredients is limited by authenticated users."""

        other_user = create_dummy_user(
            email="other_user_ingredient@example.com")
        Ingredient.objects.create(user=other_user, name='cother cocacola')
        Ingredient.objects.create(user=other_user, name='other bakery')

        Ingredient.objects.create(user=self.user, name='cola-cola')
        Ingredient.objects.create(user=self.user, name='bakery')

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(len(serializer.data), 2)
        self.assertEqual(ingredients.data, serializer.data)
