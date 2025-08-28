# from django.urls import path
# from . import views

# urlpatterns=[
#     path('test_template/',views.test_template,name = 'test_template'),
#     path('start_test/<int:question_id>/', views.start_test, name='start_test'),
#     path('question/<int:question_id>/', views.show_question, name='show_question'),
#     path('submit_answer/<int:question_id>/', views.submit_answer, name='submit_answer'),
#     # urls.py
#     path('view_score/', views.score, name='view_score'),


# ]    
from django.urls import path
from . import views

urlpatterns = [
    path('test_template/',views.test_template,name = 'test_template'),
    path('take_test/', views.take_test, name='take_test'),
    path('get_questions/', views.get_questions, name='get_questions'),
    path('submit_answer/', views.submit_answer_ajax, name='submit_answer_ajax'),
    # path('view_score/', views.view_score, name='view_score'),
]

