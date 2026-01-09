from django.urls import path
from . import views

urlpatterns = [
    path('', views.test_dashboard, name='test_dashboard'), 
    path('course/<int:course_id>/', views.course_quizzes, name='course_quizzes'),
    path('take/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
]