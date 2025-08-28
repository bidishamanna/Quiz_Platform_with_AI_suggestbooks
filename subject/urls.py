from django.urls import path
from . import views

urlpatterns=[
    path("", views.subject_list, name="subject_list"),
    path('add_subject/', views.add_subject, name='add_subject'),
    path("edit/<int:pk>/", views.edit_subject, name="edit_subject"),
    path('delete/<int:pk>/',views.delete_subject,name='delete_subject'),
    path('get_rows/',views.get_subject_rows,name = 'get_subject_rows'),
    path('recycle-bin/', views.subject_recycle_bin, name='subject_recycle_bin'),
    path('restore/<int:pk>/', views.restore_subject, name='restore_subject'),
  
]




