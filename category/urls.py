from django.urls import path
from . import views

urlpatterns=[
    path("", views.category_list, name="category_list"),
    path('add/', views.add_category, name='add_category'),
    path("edit/<int:pk>/", views.edit_category, name="edit_category"),
    path("delete/<int:pk>/", views.delete_category, name="delete_category"),
    
    path('get_rows/',views.get_category_rows,name = 'get_category_rows'),
    path("recycle_bin/", views.recycle_bin, name="recycle_bin"), 
    path("restore/<int:pk>/", views.restore_category, name="restore_category"),
]


