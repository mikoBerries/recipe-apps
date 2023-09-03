"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        # fields = "__all__"
        fields = ['id', 'title', 'time_munites',
                  'price', 'link', 'create_on', 'update_on', 'tags']
        read_only_fields = ['id', 'create_on', 'update_on']
        # exclude = ['id']

    def create(self, validate_data):
        """Create a recipe"""
        # Overriding create function for recipe
        tags = validate_data.pop('tags', [])
        recipe = Recipe.objects.create(**validate_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user, **tag,
            )
            recipe.tags.add(tag_obj)

        # recipe will created when recipe queryset used
        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Detail recipes."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
