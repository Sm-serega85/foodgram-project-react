import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = ' Загрузка тегов и ингредиентов '

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Загружаются тэги'))
        Tag.objects.get_or_create(
            name='Завтрак',
            slug='breakfast',
            color='#FFFC66'
        )
        Tag.objects.get_or_create(
            name='Обед',
            slug='lunch',
            color='#54E709'
        )
        Tag.objects.get_or_create(
            name='Ужин',
            slug='dinner',
            color='#E4007C'
        )
        self.stdout.write(self.style.WARNING('Загружаются ингредиенты'))
        with open('data/ingredients.csv',
                  encoding='utf-8') as fixture:
            reader = csv.reader(fixture)
            for row in reader:
                name, unit = row
                Ingredient.objects.get_or_create(name=name,
                                                 measurement_unit=unit)
