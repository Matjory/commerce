from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('listing/<int:listing_id>/', views.listing_detail, name='listing_detail'),
    path('create_listing/', views.create_listing, name='create_listing'),
    path('add_comment/<int:listing_id>/', views.add_comment, name='add_comment'),
    path('login/', views.login_view, name='login'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
]
