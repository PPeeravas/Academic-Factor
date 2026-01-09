from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from courses.models import Course, Enrollment # Ensure Enrollment is imported
from .models import Quiz

# 1. Dashboard: Show Courses
def test_dashboard(request):
    # In a real app, filter this by courses the user has bought:
    # courses = request.user.enrolled_courses.all()
    courses = Course.objects.all() 
    return render(request, 'quizzes/dashboard.html', {'courses': courses})

# 2. Quiz List: Show Quizzes for a selected Course
def course_quizzes(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    quizzes = course.quizzes.all()
    return render(request, 'quizzes/quiz_list.html', {'course': course, 'quizzes': quizzes})

    # 3. Take Quiz: Show Questions
@login_required # <--- 1. Require Login
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course # Get the course this quiz belongs to

    # ===================================================
    # 🔒 SECURITY CHECK: IS USER ENROLLED?
    # ===================================================
    enrollment = Enrollment.objects.filter(
        user=request.user, 
        course=course,
        expires_at__gt=timezone.now()
    ).first()
    
    if not enrollment:
        messages.error(request, "Access Denied: You must enroll in the course to take this quiz.")
        # Redirect back to the course detail page so they can buy it
        return redirect('course_detail', course_id=course.id)
    # ===================================================

    return render(request, 'quizzes/take_quiz.html', {'quiz': quiz})