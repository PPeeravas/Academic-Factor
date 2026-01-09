# courses/admin.py
from django.contrib import admin
from .models import Course, CourseVideo, CoursePDF, PastPaper


class VideoInline(admin.TabularInline):
    model = CourseVideo
    extra = 1

class PDFInline(admin.TabularInline):
    model = CoursePDF
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'teacher')
    inlines = [VideoInline, PDFInline]

@admin.register(PastPaper)
class PastPaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_at')
    search_fields = ('title', 'category')