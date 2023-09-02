"""
Test for recipe APIs.
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe

# from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def create_recipe(user, **params):
    """Create and return a sample recipe."""

    # default values
    defaults = {
        'title': 'sample recipe title',
        'time_munites': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://exmaple.com/recipe.pdf',
    }
    # update defaults dictonary with incoming params
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **params)
    return recipe


class PublicRecipeAPITests(TestCase):
    """Test un-authenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required to call API."""
        response = self.client.get(RECIPE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test aunthenticated API request."""

    def setUp(self):
        self.client = APIClient()
        # setUp before test class started
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )

        # authenticate using create user
        self.client = APIClient
        self.client.force_authenticate(user=self.user)

    def test_retrive_recipes(self):
        """Test retrive a list of recipes."""

        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass123',
        )

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
