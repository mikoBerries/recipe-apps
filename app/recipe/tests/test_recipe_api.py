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

from recipe.serializer import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPE_URL = reverse('recipe:recipe-list')


def create_dummy_user(**params):
    """Create and return a new user for testing."""
    return get_user_model().objects.create_user(**params)


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


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

    recipe = Recipe.objects.create(user=user, **defaults)
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
        # setUp before test class started
        self.user = create_dummy_user(
            email='testing@example.com',
            password='testpass123'
        )

        # authenticate using create user
        self.client = APIClient()
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
        other_user = create_dummy_user(
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

    def test_get_recipe_detail(self):
        """test get recipe detail."""

        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""

        payload = {
            'title': 'sample recipe title',
            'time_munites': 22,
            'price': Decimal('5.25'),
            # 'description': 'Sample description',
            # 'link': 'http://exmaple.com/recipe.pdf',
        }
        response = self.client.post(RECIPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check created recipe in database with payload
        recipe = Recipe.objects.get(id=response.data['id'])
        self.assertEqual(recipe.user, self.user)
        # loop other values
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = 'https://example.com/recipe.pdf'

        recipe = create_recipe(
            user=self.user,
            title='sample title',
            link=original_link,
        )

        payload = {'title': 'New recipe title'}

        url = detail_url(recipe.id)
        respone = self.client.patch(url, payload)

        self.assertEqual(respone.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of a recipe."""

        recipe = create_recipe(
            user=self.user,
            title='sample recipe title',
            link='http://exmaple.com/recipe.pdf',
            description='sample recipe description'
        )
        payload = {
            'title': 'new recipe title',
            'time_munites': 100,
            'price': Decimal('2.25'),
            'description': 'this is a new description',
            'link': 'http://exmaple.com/new-recipe.pdf',
        }

        url = detail_url(recipe.id)
        respone = self.client.put(url, payload)

        self.assertEqual(respone.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_update_user_return_error(self):
        """Test changing the recipe user result in a error."""

        new_user = create_dummy_user(
            email='user2@example.com', password='thisispassword')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)

        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipes return success."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        response = self.client.delete(url)

        # Delete status code for django are (HTTP 204 NO CONTENT
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        data_exist = Recipe.objects.filter(id=recipe.id).exists()
        self.assertFalse(data_exist)

    def test_delete_other_users_recipe_error(self):
        """Test trying to delete other users recipes, and raise a error."""
        new_user = create_dummy_user(
            email='user3@example.com', password='thisispassword')

        recipe = create_recipe(user=new_user)
        url = detail_url(recipe.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        data_exist = Recipe.objects.filter(id=recipe.id).exists()
        self.assertTrue(data_exist)
