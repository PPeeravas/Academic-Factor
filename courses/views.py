from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages   
from django.db.models import Q
from django.utils import timezone
from .models import Course, PastPaper, Enrollment

@login_required
def manage_students(request):
    # We use 'course__instructor' (Two underscores) because your model uses 'instructor' on line 11
    enrollments = Enrollment.objects.filter(
        course__instructor=request.user 
    ).select_related('course', 'user').distinct()
    
    return render(request, 'courses/manage_students.html', {'enrollments': enrollments})


@login_required
def revoke_access(request, enrollment_id):
    if request.method == 'POST':
        # 1. Get the specific enrollment ID from the button click
        # Do NOT filter by request.user here, or you can only delete yourself!
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
        
        user_name = enrollment.user.username
        course_obj = enrollment.course
        student_obj = enrollment.user

        # 2. Delete from Enrollment table (Stops video access)
        enrollment.delete()

        # 3. IMPORTANT: Also remove them from the Course.students ManyToMany field
        # If they remain in the students list, 'is_enrolled' might stay True in some views
        if student_obj in course_obj.students.all():
            course_obj.students.remove(student_obj)
        
        messages.warning(request, f"Access revoked for {user_name} from {course_obj.title}.")
    
    return redirect('manage_students')

def courses_list(request):
    courses = Course.objects.all()
    # Path: courses/templates/courses/course_list.html
    return render(request, 'courses/course_list.html', {'courses': courses})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    is_enrolled = False
    # Use user.is_authenticated to check if we should even query the DB
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user, 
            course=course,
            expires_at__gt=timezone.now()
        ).exists()

    context = {
        'course': course,
        'is_enrolled': is_enrolled,
    }
    # Path: courses/templates/courses/course_detail.html
    return render(request, 'courses/course_detail.html', context)

def past_papers(request):
    query = request.GET.get('q')
    
    if query:
        papers = PastPaper.objects.filter(
            Q(title__icontains=query) | 
            Q(category__icontains=query)
        )
    else:
        papers = PastPaper.objects.all().order_by('-uploaded_at')
        
    # Path: courses/templates/courses/past_papers.html
    return render(request, 'courses/past_papers.html', {'papers': papers})