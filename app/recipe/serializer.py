"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Recipe
        fields = "__all__"
        read_only_fields = ['id']
        # fields = ['id','title','time_minutes','price','link']
        # exclude = ['id']
