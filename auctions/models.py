from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    pass

class Listing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings", blank=True, null=True)
    title = models.CharField(max_length=96, blank=False, null=False)
    description = models.CharField(max_length=1024, blank=True)
    # If user does not provide a starting date and time, use NOW as default
    start = models.DateTimeField(default=timezone.now, blank=False, null=False)
    end = models.DateTimeField(blank=False, null=False)
    start_price = models.DecimalField(max_digits=8, decimal_places=2 ,blank=False, null=False)
    image = models.URLField(max_length=1024, blank=True)
    category = models.CharField(max_length=96, blank=True, null=True)

class Bid(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids",blank=True, null=True)
    auction = models.ForeignKey(Listing,blank=True, null=True, on_delete=models.CASCADE, related_name="bidders")
    bid = models.DecimalField(max_digits=8, decimal_places=2 ,blank=True, null=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", blank=True, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments", blank=True, null=True)
    content = models.CharField(max_length=1024, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now, blank=False, null=False)

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishers", blank=True, null=True)
    item = models.ForeignKey(Listing,blank=True, null=True, on_delete=models.CASCADE, related_name="wishes")