from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from courses.models import Course


def home(request):
    # Get the first 6 courses from the database
    courses = Course.objects.all()[:6] 
    
    return render(request, 'pages/home.html', {
        'courses': courses
    })

@login_required
def home_view(request):
    courses = Course.objects.all()
    # Ensure this points to the correct template path
    return render(request, 'pages/index.html', {'courses': courses})