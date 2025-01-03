from django.contrib import admin

from .models import User, Listing, Bid, Comment, Wishlist


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "password")

class ListingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Listing._meta.fields]

class BidAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Bid._meta.fields]

class CommentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Comment._meta.fields]

class WishlistAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Wishlist._meta.fields]


admin.site.register(User, UserAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Wishlist, WishlistAdmin)