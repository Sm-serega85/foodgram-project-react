from api.views import (
    TagsViewSet,
    IngredientsViewSet,
    RecipesViewSet
)
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import UsersViewSet

router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'recipes', RecipesViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken'))
]
