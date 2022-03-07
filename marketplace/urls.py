from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("search", views.search, name="search"),
    path("about", views.help, name="help"),
    path("product/<str:id>", views.product, name="product"),
    path("<str:id>/back", views.back, name="back"),
    path("<str:id>/cart", views.cart, name="cart"),
    path("<str:id>/cart/confirm", views.cartConfirm, name="cartConfirm"),
    path("<str:id>/cart/<str:pid>/add", views.cartAdd, name="cartAdd"),
    path("<str:id>/cart/<str:cid>/remove", views.cartRemove, name="cartRemove"),
    path("<str:id>/market", views.market, name="market"),
    path("<str:id>/market/add", views.addProduct, name="addProduct"),
    path("<str:id>/market/<str:pid>/edit", views.editProduct, name="editProduct"),
    path("<str:id>/market/<str:pid>/delete", views.deleteProduct, name="deleteProduct"),
    path("<str:id>/market/<str:pid>/add", views.marketAdd, name="marketAdd"),
    path("<str:id>/market/<str:mid>/remove", views.marketRemove, name="marketRemove"),
    path("<str:id>", views.account, name="account"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
