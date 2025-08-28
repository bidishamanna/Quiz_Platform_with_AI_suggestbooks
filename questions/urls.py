

from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_question, name='add_question'),
    path('get_subjects/<int:category_id>/', views.get_subjects_by_category, name='get_subjects_by_category'),
    path('get_sets/<int:category_id>/', views.get_sets_by_category, name='get_sets_by_subject'),
    path('list/', views.question_list, name='question_list'),
    # path('get_row/<int:question_id>/', views.get_question_row, name='get_question_row'), # for table display 
    path('edit/<int:pk>/', views.edit_question, name='edit_question'),
    path('delete/<int:pk>/', views.delete_question, name='delete_question'),
     # ♻️ Recycle Bin for Questions (Page View)
    path('recycle_bin/', views.question_recycle_bin, name='question_recycle_bin'),

    # 🔁 Restore Deleted Question (AJAX POST)
    path('restore/<int:pk>/', views.restore_question, name='restore_question'),
    path('upload-questions/', views.upload_questions, name='upload_questions'),
    path("get_rows/", views.get_question_rows, name="get_question_rows"),
   

    # path('start/', views.start_test_page, name='start_test'),
    # path('assign-random-set/', views.assign_random_set, name='assign_random_set'),
    # path('get-question/', views.get_question, name='get_question'),
    # path('submit-answer/', views.submit_answer, name='submit_answer'),

    # Load start test page
    path("start-test/<slug:slug>/", views.start_test, name="start_test"),


    # Init attempt API
    path("init-attempt/<slug:slug>/", views.init_attempt, name="init_attempt"),

    # Get next question
    path("get-question/", views.get_question, name="get_question"),

    # Submit answer
    path("submit-answer/", views.submit_answer, name="submit_answer"),

    # Final result for AJAX
    path("result/<int:attempt_id>/", views.result, name="result"),

    # Review results page
    path("review/<int:attempt_id>/", views.review_attempt, name="review_attempt"),

    path('books/suggest/', views.suggest_books_for_subject, name='suggest_books_for_subject'),


]



