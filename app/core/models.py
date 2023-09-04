"""
Database models.
"""

from django.conf import Settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Manager for user."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return new user."""
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # objects to held costume user manager when save UserManager()
    objects = UserManager()

    USERNAME_FIELD = "email"


class Recipe(models.Model):
    """Recipe models object."""
    user = models.ForeignKey(
        # Settings.__getattribute__("USERMODEL"),
        # getattr(Settings, "USERMODEL", None),
        User,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_munites = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)

    # create_on will auto fill by.save() wheen first data created
    create_on = models.DateTimeField(auto_now_add=True, null=True)
    # update on will autol fill by .save when data is selected and updated vai .save()
    update_on = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')

    def __str__(self) -> str:
        return self.title


class Tag (models.Model):
    """Tag for filtering recipe."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """Ingredient for recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return self.name
