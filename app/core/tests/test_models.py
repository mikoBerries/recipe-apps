"""
Test for models.
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch

from core import models


def create_user(email='user_tag_model@example.com', password='thisispassowrd'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


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

    def test_create_recipe(self):
        """Test create a recipe is successful."""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpass1234',
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),
            description='sample recipe description.',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a tag successfull."""
        user = create_user()

        tag = models.Tag.objects.create(user=user, name='tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating a ingredient successfull."""
        user = create_user()

        ingredient = models.Ingredient.objects.create(
            user=user, name='Ingredient_1')

        self.assertEqual(str(ingredient), ingredient.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
