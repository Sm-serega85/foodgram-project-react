from api.serializers import UsersSerializer, SubscribeSerializer
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.response import Response

from .models import CustomUser, Subscribe


class UsersViewSet(UserViewSet):
    """ModelViewSet для Пользователя на основе UserViewSet из Djoser бибилиотеки."""
    queryset = CustomUser.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        """Функция оформления подписки."""
        user = request.user
        author = get_object_or_404(CustomUser, id=id)

        if request.method == 'POST':
            serializer = SubscribeSerializer(author, data=request.data,
                                             context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            Subscribe.objects.filter(user=user, author=author).delete()
            return Response({'detail': 'Вы отписались от этого автора!'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """Функция вывода подписок."""
        queryset = CustomUser.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
