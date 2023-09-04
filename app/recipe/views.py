"""
Views for recipe API
"""

from rest_framework import viewsets, mixins, status

from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializer


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""
    serializer_class = serializer.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrive recipes for authenciated user."""
        # return super().get_queryset()
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return speicifcy serializer class for each request."""

        # return super().get_serializer_class()
        if self.action == 'list':  # is url list called
            return serializer.RecipeSerializer
        elif self.action == 'upload_image':  # if upload_image called
            return serializer.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    # Create a new costum action excluding from CRUD in viewset
    # if detail is true then url must including from base url {id}
    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to incoming recipe."""
        recipe = self.get_object()
        # serizalie incoming object
        serializer = self.get_serializer(recipe, data=request.data)

        # check validation of incoming request that populate in choosen serizalier
        if serializer.is_valid():
            # save data and create django style response data
            serializer.save()
            # will return saved serializer object with status HTTP 200
            return Response(serializer.data, status=status.HTTP_200_OK)

        # returning error in each fileds with status HTTP 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for recipe attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtering queryset to authenticated user only."""
        # will filtering Tag data with incoming user request.
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """View for tag in the database."""
    serializer_class = serializer.TagSerializer
    queryset = Tag.objects.all()

    # Refactoring with BaseRecipeAttrViewSet

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     """Filtering queryset to authenticated user only."""
    #     # will filtering Tag data with incoming user request.
    #     return self.queryset.filter(user=self.request.user).order_by('-name')


class IngredientViewSet(BaseRecipeAttrViewSet):
    """"View for ingredients."""
    serializer_class = serializer.IngredientSerializer
    queryset = Ingredient.objects.all()
    # Refactoring with BaseRecipeAttrViewSet

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    # def get_queryset(self):
    #     """Filtering queryset to authenticated user only."""
    #     # will filtering Tag data with incoming user request.
    #     return self.queryset.filter(user=self.request.user).order_by('-name')
