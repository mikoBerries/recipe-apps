"""
Test for recipe APIs.
"""
import tempfile
import os

from PIL import Image

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe, Tag, Ingredient

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


def image_upload_url(recipe_id):
    """Create and return an image upload URL."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

    def test_create_recipe_with_new_tag(self):
        """Test creating a new Recipe with new Tag."""

        payload = {
            'title': 'Vannila ice cream',
            'time_munites': 100,
            'price': Decimal('10.25'),
            'tags': [{'name': 'cold'}, {'name': 'vannila'}],
            'description': 'This is a ice cream',
            'link': 'http://exmaple.com/ice_cream.pdf',
        }

        response = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check created recipe in database with payload
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        for tag in payload['tags']:
            tag_existed = recipe.tags.filter(
                name=tag['name'], user=self.user).exists()
            self.assertTrue(tag_existed)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tags."""
        tag_indian = Tag.objects.create(user=self.user, name='indian')
        payload = {
            'title': 'Pongal',
            'time_munites': 100,
            'price': Decimal('10.25'),
            'tags': [{'name': 'indian'}, {'name': 'Hot'}],
            'description': 'this is indian food',
            'link': 'http://exmaple.com/pongal.pdf',
        }

        response = self.client.post(RECIPE_URL, payload, format='json')

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)

        self.assertIn(tag_indian, recipe.tags.all())

        for tag in payload['tags']:
            tag_existed = recipe.tags.filter(
                name=tag['name'], user=self.user).exists()
            self.assertTrue(tag_existed)

    def test_create_tag_on_update(self):
        """Test create tag when updating a recipe."""
        recipe = create_recipe(user=self.user)

        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')

        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')

        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tags."""
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredient(self):
        """Test creating a new Recipe with new ingredient."""

        payload = {
            'title': 'Ratatoui',
            'time_munites': 60,
            'price': Decimal('120.25'),
            'ingredients': [{'name': 'Potato'}, {'name': 'Chocolate'}],
            'description': 'This is a ice cream',
            'link': 'http://exmaple.com/ratatoui.pdf',
        }

        response = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check created recipe in database with payload
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        # check is every ingredient in payload craeted ?
        for ingredient in payload['ingredients']:
            ingredient_existed = recipe.ingredients.filter(
                name=ingredient['name'], user=self.user
            ).exists()
            self.assertTrue(ingredient_existed)

    def test_create_recipe_with_existing_ingredient(self):
        """Test creating a new Recipe with existing ingredient."""
        payload = {
            'title': 'Ratatoui',
            'time_munites': 60,
            'price': Decimal('120.25'),
            'ingredients': [{'name': 'Potato'}, {'name': 'Chocolate'}, {'name': 'Lemon'}],
            'description': 'This is a ice cream',
            'link': 'http://exmaple.com/ratatoui.pdf',
        }

        existed_ingredient = Ingredient.objects.create(
            user=self.user, name='Lemon')
        # payload['ingredients'].append(existed_ingredient)

        response = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check created recipe in database with payload
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 3)
        self.assertIn(existed_ingredient, recipe.ingredients.all())
        # check is every ingredient in payload craeted ?
        for ingredient in payload['ingredients']:
            ingredient_existed = recipe.ingredients.filter(
                name=ingredient['name'], user=self.user
            ).exists()
            self.assertTrue(ingredient_existed)

    def test_update_recipe_ingredient_on_update(self):
        """Test creating  an ingredient when updating a recipe."""
        recipe = create_recipe(user=self.user)

        payload = {'ingredients': [{'name': 'Lemon'}]}

        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_inggredient = Ingredient.objects.get(
            user=self.user, name='Lemon')
        self.assertIn(new_inggredient, recipe.ingredients.all())

    def test_update_recipe_Assign_ingredient(self):
        """Test assigning an existing inggredient when updating a recipes."""
        ingredient1 = Ingredient.objects.create(user=self.user, name='pepper')

        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(user=self.user, name='chilli')
        payload = {'ingredients': [{'name': 'chilli'}]}

        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing a recipes ingredients."""
        ingredient = Ingredient.objects.create(user=self.user, name='ice')
        ingredient2 = Ingredient.objects.create(user=self.user, name='sugar')

        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient, ingredient2)

        url = detail_url(recipe.id)
        payload = {'ingredients': []}
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)


class ImageUploadTest(TestCase):
    """Test for image upload API."""

    def setUp(self):
        # setUp before test class started
        self.user = create_dummy_user(
            email='testing@example.com',
            password='testpass123'
        )

        # authenticate using create user
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        # tear down will execute after every test case done
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading a image to a recipe."""
        url = image_upload_url(self.recipe.id)

        # using tempfile.NamedTemporaryFile to make name image file with diffent suffix
        with tempfile.NamedTemporaryFile(suffix='.jpg')as image_file:
            # using PIL.Image to make dummy images.
            img = Image.new('RGB', (10, 10))
            # Write img data to image_file
            img.save(image_file, format='JPEG')
            # change cursor pointer to start (just in case)
            image_file.seek(0)

            payload = {'image': image_file}
            response = self.client.post(url, payload, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # refresh updated local data match to DB
        self.recipe.refresh_from_db()
        # cehck are image is created and returned in response.body from post url
        self.assertIn('image', response.data)
        # checking is file are created in static file on starting server?
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_rquest(self):
        """Test uploading a image to a recipe returned Bad request."""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'This is just a string data'}
        response = self.client.post(url, payload, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
