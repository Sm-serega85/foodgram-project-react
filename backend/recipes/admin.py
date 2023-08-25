from django.contrib import admin

from .models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientInRecipe,
    Favorite,
    ShoppingCart
)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name')
    list_filter = ('author', 'name', 'tags')
    exclude = ('ingredients',)

    inlines = [
        RecipeIngredientInline,
    ]


admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientInRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
