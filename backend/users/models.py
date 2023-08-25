from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Кастом-модель Пользователя."""
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='E-mail',
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Никнейм',
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия',
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email',
            )
        ]

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписок на автора рецептов."""
    user = models.ForeignKey(
        CustomUser,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='На кого подписываются'
    )

    class Meta:
        ordering = ('-author_id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe',
            )
        ]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
