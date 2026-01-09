# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # --- Authentication & Registration ---
    path('register/', views.register_view, name='register'),
    
    # OLD: verify_phone_view (Deleted)
    # NEW: verify_registration_otp (Use this instead)
    path('verify-otp/', views.verify_registration_otp, name='verify_registration_otp'), 
    # Note: I changed the name in the path to keep it generic, or you can keep 'verify-otp'

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- Password Reset ---
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-reset-otp/', views.verify_reset_otp_view, name='verify_reset_otp'),
    path('reset-password/', views.reset_new_password_view, name='reset_new_password'),

    # --- Courses & Lessons ---
    path('courses/', views.courses, name='courses'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/test/', views.course_test_secure, name='course_test'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('courses/<int:course_id>/learn/', views.lesson_view, name='lesson'),
    path('courses/<int:course_id>/checkout/', views.payment_checkout, name='payment_checkout'),
    path('courses/<int:course_id>/payment-success/', views.payment_success, name='payment_success'),
    
]