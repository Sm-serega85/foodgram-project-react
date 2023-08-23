from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Tag,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Favorite,
    ShoppingCart,
)
from rest_framework import serializers, status
from rest_framework.validators import UniqueTogetherValidator
from users.models import (
    CustomUser,
    Subscribe
)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для Тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для Ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class UsersSerializer(UserSerializer):
    """Сериализатор для Пользователя."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj).exists()


class UsersCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания Пользователя."""
    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'password', 'username', 'first_name', 'last_name')


class SubscribeSerializer(UsersSerializer):
    """Сериализатор для Подписки на других пользователей."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = UsersSerializer.Meta.fields + (
            'recipes_count', 'recipes'
        )
        read_only_fields = ['email', 'username', 'first_name', 'last_name']

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                detail='У вас уже есть подписка на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise serializers.ValidationError(
                detail='Подписаться на самого себя нельзя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецептах."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов в рецептах."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания Рецепта."""
    author = UsersSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags',
                  'image', 'name', 'text', 'cooking_time')

    def validate_ingredients(self, data):
        ingredients_ids = [ingredient['id'].id for ingredient in data]
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                detail='Ингредиент должен быть уникальным!',
                code=status.HTTP_400_BAD_REQUEST
            )
        for ingredient in data:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    detail='Кол-во ингредиента должно быть больше 0!',
                    code=status.HTTP_400_BAD_REQUEST
                )
        return data

    def validate_tags(self, data):
        if not data:
            raise serializers.ValidationError(
                detail='Выберите хотя бы один тег!',
                code=status.HTTP_400_BAD_REQUEST
            )
        tags_ids = [tag.id for tag in data]
        if len(tags_ids) != len(set(tags_ids)):
            raise serializers.ValidationError(
                detail='Тег должен быть уникальным!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def add_ingredients(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create([IngredientInRecipe(
            ingredient=ingredient['id'],
            recipe=recipe,
            amount=ingredient['amount']
        ) for ingredient in ingredients])

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.get('tags')
        ingredients = validated_data.get('ingredients')
        recipe.image = validated_data.get('image', recipe.image)
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get('cooking_time',
                                                 recipe.cooking_time)
        if ingredients:
            recipe.ingredients.clear()
            self.add_ingredients(ingredients, recipe)
        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)
        recipe.save()
        return recipe

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(instance, context=context).data


class RecipeSerializer(serializers.ModelSerializer):
    """Простой сериализатор для отображения Рецептов."""
    name = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения Рецептов."""
    author = UsersSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True, source='IngredientInRecipe'
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        user = request.user
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        user = request.user
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецепта в Избранное."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = (
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'recipe'),
                message='Данный рецепт уже в избранном!'
            ),
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        recipe = instance.recipe
        return RecipeSerializer(recipe, context=context).data


class ShoppingCartSerializer(FavoriteRecipeSerializer):
    """Сериализатор для добавления рецепта в Корзину покупок."""
    class Meta(FavoriteRecipeSerializer.Meta):
        model = ShoppingCart
        validators = (
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('user', 'recipe'),
                message='Данный рецепт уже в корзине!'
            ),
        )

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        recipe = instance.recipe
        return RecipeSerializer(recipe, context=context).data
