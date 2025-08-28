from django.urls import path
from . import views

urlpatterns=[
    path("registration/", views.registration, name="registration"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login_view/', views.login_view, name='login_view'),
    path("logout_view/", views.logout_view, name="logout_view"),
    path("staff_dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("student_dashboard/", views.student_dashboard, name="student_dashboard"),
    # path('account/check-email/', views.check_email_exists, name='check_email'),
    path('check_email/', views.check_email_unique, name='check_email'),
    # path('check-login-status/', views.check_login_status, name='check_login_status'),
    # Add your start-test path too
    # path('start-test/<int:subject_id>/', views.start_test, name='start_test'),


    # forget password
    
    path('forget_password/', views.forget_password, name="forget_password"),
    path('newpassword/<str:email>/', views.newpassword, name='newpassword'),

    path('profile',views.my_profile,name = 'my_profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    

]



