from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from marketplace.models import Account, Product, Market, Cart, Ownership


class AccountAdmin(UserAdmin):
    list_display = ('username', 'email', 'password', 'date_joined', 'last_login', 'is_admin', 'is_staff')
    search_fields = ('email', 'username')
    readonly_fields = ('id', 'date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "user", "description", "quantity", "recommend", "price", "category"]
    search_fields = ('name',)
    list_filter = ["user", "category"]
    readonly_fields = ('id', 'recommend')

class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "product", "quantity"]
    list_filter = ["user", "product"]
    readonly_fields = ('id',)

class MarketAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "product"]
    list_filter = ["user"]
    readonly_fields = ('id',)

class OwnershipAdmin(admin.ModelAdmin):
    list_display = ["id", "seller", "buyer", "product", "quantity", "date_buy"]
    list_filter = ["seller", "buyer", "product", "date_buy"]
    readonly_fields = ('id', 'date_buy')

# Register your models here.
admin.site.register(Account, AccountAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Market, MarketAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Ownership, OwnershipAdmin)
