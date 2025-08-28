from django.urls import path
from . import views

urlpatterns=[
    
    path('', views.home, name='home'),
    # path('category/<int:category_id>/', views.category_view, name='category_view'),
    # path('category/<int:category_id>/sets/', views.get_sets, name='get_sets'),
    # path('category/<slug:category_slug>/sets/', views.get_sets, name='get_sets'),
    path('category/<slug:category_slug>/sets/', views.category_sets_page, name='category_sets_page'),

    path("contact/",views.contact,name = "contact"),
    path("about/",views.about,name = "about"),
    # path("leaderboard/", views.leaderboard_view, name="leaderboard"),
      path("home-leaderboard/", views.home_leaderboard_view, name="home_leaderboard"),
    
]    
