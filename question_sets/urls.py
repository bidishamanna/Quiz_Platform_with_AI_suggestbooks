from django.urls import path
from . import views

urlpatterns=[
    path("", views.set_list, name="set_list"),
    path('add/', views.add_set, name='add_set'),
    path("edit/<int:pk>/", views.edit_set, name="edit_set"),
    path("delete/<int:pk>/", views.delete_set, name="delete_set"),
    
  
    path("recycle-bin/", views.set_recycle_bin, name="set_recycle_bin"),
    path("restore/<int:pk>/", views.restore_set, name="restore_set"),
    path("get_rows/", views.get_set_rows, name="get_set_rows"),

]



