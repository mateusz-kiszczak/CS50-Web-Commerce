from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("wishlist", views.wishlist, name="wishlist"),
    path("past", views.past, name="past"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:query>", views.categories_query, name="categories_query")
]
