
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('category/',include('category.urls')),
    path('questions/',include('questions.urls')),
    path('account/',include('account.urls')),
    path('',include('about.urls')),
    path("subject/",include('subject.urls')),
    path('question_sets/',include('question_sets.urls')),
    path('quiz/',include('quiz.urls')),
    # path('payment/',include('payment.urls')),
    path('cart/',include('cart.urls')),

]




