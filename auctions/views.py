from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Listing, Category, Watchlist, Bid, Comment
from .forms import ListingForm, BidForm, CommentForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError

def index(request):
    listings = Listing.objects.all()
    categories = Category.objects.all()  
    return render(request, "auctions/index.html", {
        "listings": listings,
        "categories": categories  
    })

@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creator = request.user
            listing.current_price = listing.starting_bid
            listing.save()
            return redirect('index')
    else:
        form = ListingForm()
    return render(request, "auctions/create_listing.html", {"form": form})

def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    comments = listing.comments.all()
    bid_form = BidForm()
    comment_form = CommentForm()

    if request.method == "POST":
        if 'place_bid' in request.POST:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                new_bid = bid_form.cleaned_data['bid_amount']
                if new_bid > listing.current_price:
                    listing.current_price = new_bid
                    listing.save()
                    Bid.objects.create(user=request.user, listing=listing, bid_amount=new_bid)
                    return redirect('listing_detail', listing_id=listing_id)
                else:
                    bid_form.add_error('bid_amount', 'Your bid must be higher than the current price.')
        
        elif 'add_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.user = request.user
                new_comment.listing = listing
                new_comment.save()
                return redirect('listing_detail', listing_id=listing_id)

    context = {
        "listing": listing,
        "comments": comments,
        "bid_form": bid_form,
        "comment_form": comment_form,
        "in_watchlist": request.user.is_authenticated and Watchlist.objects.filter(user=request.user, listing=listing).exists(),
    }
    return render(request, "auctions/listing.html", context)

@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.listing = listing
            comment.save()
            return redirect('listing_detail', listing_id=listing_id)
    return redirect('listing_detail', listing_id=listing_id)

@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    Watchlist.objects.get_or_create(user=request.user, listing=listing)
    return redirect('listing_detail', listing_id=listing_id)

@login_required
def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    Watchlist.objects.filter(user=request.user, listing=listing).delete()
    return redirect('listing_detail', listing_id=listing_id)

@login_required
def watchlist(request):
    listings = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {"listings": [item.listing for item in listings]})

def category_list(request):
    categories = Category.objects.all()
    print("Categories:", categories)
    return render(request, "auctions/categories.html", {"categories": categories})

def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/category_detail.html", {"category": category, "listings": listings})

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {"message": "Invalid username and/or password."})
    return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {"message": "Passwords must match."})
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {"message": "Username already taken."})
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/register.html")
