from django.db import models
from courses.models import Course

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    # This TextField allows teachers to write raw LaTeX code
    problem_text = models.TextField(help_text="Write Math here using LaTeX! Example: $x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$")
    answer_text = models.TextField(help_text="The correct answer (hidden from student initially)")
    
    def __str__(self):
        return f"Question for {self.quiz.title}"