from django.db.models import Sum
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.permissions import (
    SAFE_METHODS,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipes.models import (
    Favorite,
    ShoppingCart,
    IngredientInRecipe,
    Ingredient,
    Recipe,
    Tag,
)
from .serializers import (
    FavoriteRecipeSerializer,
    ShoppingCartSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    TagSerializer,
)
from .methods import create_shopping_cart


class IngredientsViewSet(ReadOnlyModelViewSet):
    """
    ReadOnlyModelViewSet для Ингредиентов
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class TagsViewSet(ReadOnlyModelViewSet):
    """
    ReadOnlyModelViewSet для Ингредиентов
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None


class RecipesViewSet(ModelViewSet):
    """
    ModelViewSet для Рецептов
    """
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get_serializer_class(self):
        if self.action in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        """
        Добавление/удаление рецепта в продуктовую корзину
        """
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user

        if request.method == 'POST':
            if not ShoppingCart.objects.filter(user=user.id, recipe=recipe).exists():
                serializer = ShoppingCartSerializer(
                    data={'user': user.id, 'recipe': recipe.id}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'error': 'Рецепт уже в корзине!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if ShoppingCart.objects.filter(user=user.id, recipe=recipe).exists():
            ShoppingCart.objects.filter(user=user.id, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Рецепт не в корзине!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path=r'(?P<pk>[\d]+)/favorite',
        url_name='favorite',
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, **kwargs):
        """
        Добавление/удаление рецепта в избранное
        """
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        user = request.user

        if request.method == 'POST':
            if not Favorite.objects.filter(user=user.id, recipe=recipe).exists():
                serializer = FavoriteRecipeSerializer(
                    data={'user': user.id, 'recipe': recipe.id}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'error': 'Рецепт уже в избранном!'},
                            status=status.HTTP_400_BAD_REQUEST)

        if Favorite.objects.filter(user=user.id, recipe=recipe).exists():
            Favorite.objects.filter(user=user.id, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Рецепт не в избранном!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'],
            detail=False, )
    def download_shopping_cart(self, request):
        """
        Скачивание pdf-файла с продуктами из корзины
        """
        user = request.user
        queryset = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=user
        )
        queryset_sort = queryset.values('ingredient__name',
                                        'ingredient__measurement_unit',
                                        ).annotate(
            quantity=Sum('amount')).order_by()
        return create_shopping_cart(user, queryset_sort)
