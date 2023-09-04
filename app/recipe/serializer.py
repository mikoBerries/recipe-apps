"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""
    class Meta:
        model = Tag
        fields = ['id', 'name']
        # fields = '__all__'
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        # fields = "__all__"
        fields = ['id', 'title', 'time_minutes',
                  'price', 'link', 'create_on', 'update_on', 'tags', 'ingredients']
        read_only_fields = ['id', 'create_on', 'update_on']
        # exclude = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle get/create a ingredient inside recipe."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            # created is boolean flag for data is created / not
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a recipe"""
        # Overriding create function for recipe
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)

        # Populate redundance code
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

        # auth_user = self.context['request'].user
        # for tag in tags:
        #     tag_obj, created = Tag.objects.get_or_create(
        #         user=auth_user, **tag,
        #     )
        #     recipe.tags.add(tag_obj)

        # recipe will created when recipe queryset used

    def update(self, instance, validated_data):
        """Update recipe."""
        # Overriding update recipe behavior to accpet tag too
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', [])

        # Perform clearing all tag and re-assign it
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        # Perform clearing all inggredient and re-assign it
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        # update incoming instance with updated value in validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Detail recipes."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading a images in recipe."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
