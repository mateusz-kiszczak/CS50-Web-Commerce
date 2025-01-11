from decimal import Decimal
from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from .models import User, Listing, Bid, Comment, Wishlist



#
# Functions
#

def validate_not_in_past(value): 
    if value < timezone.now(): 
        raise ValidationError("Listing's START Date can NOT be in the past.")
    
def validate_not_in_past_or_present(value): 
    if value < timezone.now(): 
        raise ValidationError("Listing's END Date must be in the future.")



#
# Form Classes
#

class NewCreateForm(forms.Form):
    title = forms.CharField(
        min_length=3,
        max_length=96, 
        widget=forms.TextInput(attrs= {
            "placeholder": "Listing Title",
        }),
        error_messages={ 
            "required": "Please enter the listing's title.",
            "min_length": "Title must be at least 3 characters long.",
            "max_length": "Title can NOT be longer than 96 characters long.",
        }
    )

    # not required, max length
    description = forms.CharField(
        required=False,
        max_length=1024,
        widget = forms.Textarea(attrs = {
            "placeholder": "Listing Description",
        })
    )

    start = forms.DateTimeField(
        label="Select listing starting date",
        widget=forms.DateTimeInput(attrs={ 
            "type": "datetime-local", 
        }),
        validators=[validate_not_in_past]
    )

    end = forms.DateTimeField(
        label="Select listing ending date",
        widget=forms.DateTimeInput(attrs={ 
            "type": "datetime-local", 
        }),
        validators=[validate_not_in_past_or_present]
    )

    start_price = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        label="Choose starting price. Min price £0.99",
        validators=[
            MinValueValidator(0.99),
            MaxValueValidator(999999.99)
        ],
        error_messages={ 
            "required": "Please enter the starting price of at least £0.99.",
            "min_value": "Starting price must be at least £0.99.",
            "max_value": "Starting price can NOT be larger than £999999.99.",
        }
    )

    image = forms.URLField(
        required=False,
        max_length=1024,
        label="Image URL",
        validators=[URLValidator()],
        error_messages={ 
            "max_length": "This URL is too long. Max valid length is 1024 characters.",
        }
    )

    category = forms.CharField(
        min_length=3,
        max_length=96, 
        error_messages={ 
            "required": "Please enter the category.",
            "min_length": "Category must be at least 3 characters long.",
            "max_length": "Category can NOT be longer than 96 characters long.",
        }

    )


class NewBidForm(forms.Form):
    bid = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        label="Enter your bid",
        validators=[
            MaxValueValidator(999999.99)
        ],
        error_messages={ 
            "required": "Please enter your bid. Your bid must be larger than current highest price",
            "max_value": "Your bid can NOT be larger than £999999.99.",
        }
    )


class NewWishlistForm(forms.Form):
    wishlist = forms.IntegerField(
        min_value=1,
        max_value=1,
        initial=1,
        widget=forms.HiddenInput()
    )


class NewEndAuctionForm(forms.Form):
    end_auction = forms.IntegerField(
        min_value=1,
        max_value=1,
        initial=1,
        widget=forms.HiddenInput()
    )


class NewCommentForm(forms.Form):
    comment = forms.CharField(
        max_length=1024,
        widget = forms.Textarea(attrs = {
            "placeholder": "Write a Comment",
        }),
        error_messages={ 
            "required": "Please enter your comment.",
            "min_length": "Your comment must be at least 3 characters long.",
            "max_length": "Your comment can NOT be longer than 1024 characters long.",
        }
    )



#
# Views Functions
#

def index(request):
    # Gat current date and time
    current_datetime = timezone.now()

    # Get all active listings, where listing's end time is greater than current time
    active_listings = Listing.objects.filter(end__gt=current_datetime).order_by("-id")

    # Get item's current price (highest bid)
    active_listings_and_current_price = active_listings.annotate(current_price=Max("bidders__bid"))

    return render(request, "auctions/index.html", {
        "listings": active_listings_and_current_price,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):
    if request.method == "POST":  
        form = NewCreateForm(request.POST)

        if form.is_valid():
            # Clean input data
            title       = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            start       = form.cleaned_data["start"]
            end         = form.cleaned_data["end"]
            start_price = form.cleaned_data["start_price"]
            image       = form.cleaned_data["image"]
            category    = form.cleaned_data["category"]

            # Create a new instance of Lisitng with cleaned data
            new_listing = Listing(
                seller = request.user,
                title = title,
                description = description,
                start = start,
                end = end,
                start_price = start_price,
                image = image,
                category = category.lower()
            )

            # Save iputs in the database.
            new_listing.save()

            # Redirect to the page with newly created listing
            return HttpResponseRedirect(reverse("listing", args=[new_listing.id]))
        else:
            return render(request, "auctions/create.html", {
                "create_form": form
            })

    return render(request, "auctions/create.html", {
        "create_form": NewCreateForm()
    })


def listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    comments = listing.comments.all()

    highest_bid_instance = Bid.objects.filter(auction=listing).order_by("-bid").first()
    highest_bid = Bid.objects.filter(auction=listing).aggregate(Max("bid"))["bid__max"]

    wishlist = None

    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user, item__id=listing_id).first()

    # Is listing active
    is_listing_active = listing.end > timezone.now()

    # Handle placing a bid
    if request.method == "POST" and "bid" in request.POST:
        form = NewBidForm(request.POST)
        
        # Validate minimum bid. Must be larger than current higher bid.
        # Or must be larger than starting price if no other bids.
        bid_valid = False
        bid = Decimal(form["bid"].value())
        error_message = ""

        if highest_bid and highest_bid < bid:
            bid_valid = True
        elif not highest_bid and listing.start_price <= bid:
            bid_valid = True
        else:
            bid_valid = False
            if highest_bid:
                error_message = f"Your bid must be larger than £{highest_bid:.2f}"
            else:
                error_message = f"Your bid must be equal or larger than £{listing.start_price:.2f}"
        
        # Seller can not bid his own auction
        if listing.seller == request.user:
            bid_valid = False
            error_message = "Your con NOT bid your own auction"

        # Buyer can not bid before auction started
        if listing.start > timezone.now():
            bid_valid = False
            error_message = "Auction has not started yet"

        if form.is_valid() and bid_valid:
            # Clean input data
            bid = form.cleaned_data["bid"]

            # Find highest bid for a specific listing and update it

            if highest_bid_instance:
                highest_bid_instance.buyer = request.user
                highest_bid_instance.bid = bid

                # Update new highest bid
                highest_bid_instance.save()

            # Else, Create a new instance of Bid if no bid exists yet
            else:
                new_bid = Bid(
                    buyer = request.user,
                    auction = listing,
                    bid = bid
                )
                
                # Save iputs in the database.
                new_bid.save()


            # Redirect to the page with newly created listing
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "highest_bid": highest_bid_instance,
                "bid_form": NewBidForm(),
                "wishlist_form": NewWishlistForm(),
                "wishlist": wishlist,
                "end_form": NewEndAuctionForm(),
                "is_listing_active": is_listing_active,
                "comment_form": NewCommentForm(),
                "comments": comments
            })
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "highest_bid": highest_bid_instance,
                "bid_form": form,
                "error_message": error_message,
                "wishlist_form": NewWishlistForm(),
                "wishlist": wishlist,
                "end_form": NewEndAuctionForm(),
                "is_listing_active": is_listing_active,
                "comment_form": NewCommentForm(),
                "comments": comments
            })

    # Handle Add and Remove from Wishlist
    if request.method == "POST" and "wishlist" in request.POST:
        # If item already inside wishlist, delete it from wishlist
        if wishlist:
            Wishlist.objects.filter(user=request.user, item__id=listing_id).delete()

            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
        # Else if not inside wishlist, add it to it.
        else:
            new_wishlist = Wishlist(
                user = request.user,
                item = listing
            )
            new_wishlist.save()

            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
        
    # Handle ending an auction
    if request.method == "POST" and "end_auction" in request.POST:
        if is_listing_active:
            # Update end date and time of listing to NOW
            listing.end = timezone.now()

            # Save changes in database.
            listing.save()

            # Redirect back to listing
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
    
    # Handle add comment
    if request.method == "POST" and "comment" in request.POST:  
        form = NewCommentForm(request.POST)

        if form.is_valid():
            # Clean input data
            comment = form.cleaned_data["comment"]

            # Create a new instance of Lisitng with cleaned data
            new_comment = Comment(
                user = request.user,
                listing = listing,
                content = comment
            )

            # Save iputs in the database.
            new_comment.save()

            # Redirect to the page with newly created listing
            return HttpResponseRedirect(reverse("listing", args=[listing_id]))
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "highest_bid": highest_bid_instance,
                "bid_form": NewBidForm(),
                "error_message": error_message,
                "wishlist_form": NewWishlistForm(),
                "wishlist": wishlist,
                "end_form": NewEndAuctionForm(),
                "is_listing_active": is_listing_active,
                "comment_form": form,
                "comments": comments
            })

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "highest_bid": highest_bid_instance,
        "bid_form": NewBidForm(),
        "wishlist_form": NewWishlistForm(),
        "wishlist": wishlist,
        "end_form": NewEndAuctionForm(),
        "is_listing_active": is_listing_active,
        "comment_form": NewCommentForm(),
        "comments": comments
    })


def past(request):
    # Gat current date and time
    current_datetime = timezone.now()

    # Get all active listings, where listing's end time is greater than current time
    past_listings = Listing.objects.filter(end__lt=current_datetime)

    # Get item's current price (highest bid)
    past_listings_and_current_price = past_listings.annotate(current_price=Max("bidders__bid"))

    return render(request, "auctions/past.html", {
        "listings": past_listings_and_current_price,
    })


def wishlist(request):
    wishlist = None

    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user).select_related("item")

    return render(request, "auctions/wishlist.html", {
        "wishlist": wishlist
    })


def categories(request):
    categories = Listing.objects.values_list("category", flat=True).distinct().order_by("category")

    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def categories_query(request, query):
    listings = Listing.objects.filter(category=query)

    return render(request, "auctions/categories.html", {
        "listings": listings,
        "query": query
    })