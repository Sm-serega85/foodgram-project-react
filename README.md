# Foodgram
"Foodgram" - это приложение, в котором пользователи могут делиться своими рецептами, подписываться на авторов и сохранять их рецепты. Также в приложении реализована продуктовая корзина, добавляя рецепт в корзину, можно скачать список продуктов, которые потребуются для приготовления этого рецепта.

## Сайт доступен по IP: 158.160.72.254
### Данные для админки:
```
Login: admin1
Email: admin1@mail.ru
Password: admin 
```

### Технологии, которые используются в сайте:

- Python
- Django
- Django REST Framework
- Docker
- PostgresQL
- Nginx

### Для корректной работы сайта в папке backend нужно создать .env файл. Пример этого файла ниже:
```
SECRET_KEY='СЕКРЕТНЫЙ КЛЮЧ DJANGO'
DEBUG=False
POSTGRES_USER=django_user
POSTGRES_PASSWORD=django_password
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
```

### Чтобы развернуть приложение в контейнерах, нужно:

- Создать .env файл, пример выше
- Сбилдить образы для frontend и backend находясь в корне проекта
```
docker build -t <username>/foodgram_frontend:latest frontend/
docker build -t <username>/foodgram_backend:latest backend/
```
- Перейти в папку /infra/ и поочередно ввести следующие команды
```
- docker-compose up -d --build
- docker-compose exec backend python manage.py migrate
- docker-compose exec backend python manage.py createsuperuser
- docker-compose exec backend python manage.py collectstatic --no-input
```

## Автор backend'a:
Сергей Смирнов