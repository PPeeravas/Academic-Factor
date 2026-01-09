from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import re  # ✅ Added for YouTube ID extraction

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='instructed_courses' 
    )
    
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='taught_courses'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_courses', blank=True)

    def __str__(self):
        return self.title

# Optional: You can keep or delete this model depending on if you still use it.
# I updated it to use YouTube URL just in case.
class CourseVideo(models.Model):
    course = models.ForeignKey(Course, related_name='videos', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    # ✅ CHANGED: Switched from FileField to URLField
    youtube_url = models.URLField(max_length=200, help_text="Enter YouTube URL") 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class CoursePDF(models.Model):
    course = models.ForeignKey(Course, related_name='pdfs', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    pdf_file = models.FileField(upload_to='course_pdfs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    
    # ✅ CHANGED: Replaced video_file with youtube_url
    youtube_url = models.URLField(
        max_length=200, 
        blank=True, 
        null=True, 
        help_text="Enter the full YouTube URL (e.g. https://www.youtube.com/watch?v=...)"
    )
    
    pdf_file = models.FileField(upload_to='courses/pdfs/', blank=True, null=True)
    content_text = models.TextField(blank=True) 
    order = models.PositiveIntegerField(default=0) 

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    # ✅ NEW: Helper function to extract ID for the template
    def get_youtube_id(self):
        """
        Extracts the ID from various YouTube URL formats.
        """
        if not self.youtube_url:
            return None
        # Regex to find ID in standard URLs and short URLs (youtu.be)
        regex = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(regex, self.youtube_url)
        return match.group(1) if match else None

class PastPaper(models.Model):
    title = models.CharField(max_length=200, help_text="e.g. A-Level Math 66")
    category = models.CharField(max_length=100, help_text="The Label. e.g. Math, Physics, PAT1")
    pdf_file = models.FileField(upload_to='past_papers/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_active(self):
        """Checks if the course is still valid (not expired)"""
        return timezone.now() < self.expires_at

    def __str__(self):
        return f"{self.user.username} -> {self.course.title}"