# courses/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # This is the line you were missing:
    path('', views.courses_list, name='courses_list'),
    
    # This is your existing detail page:
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('past-papers/', views.past_papers, name='past_papers'),
    path('manage-students/', views.manage_students, name='manage_students'),
    path('manage-students/revoke/<int:enrollment_id>/', views.revoke_access, name='revoke_access'),
]