from django.db import models
from account.models import User
from question_sets.models import Set
from category.models import Category
from subject.models import Subject
from django.db import models
from account.models import User
from subject.models import Subject
from question_sets.models import Set

class Question(models.Model):
    OPTION_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    )

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    set = models.ForeignKey(Set, on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    difficulty_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.50)
    delflag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question_text[:50]}... [Diff {self.difficulty_score}]"

class Attempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    set = models.ForeignKey(Set, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    current_index = models.IntegerField(default=0)   # linear progress
    current_difficulty = models.DecimalField(max_digits=3, decimal_places=2, default=0.50)  # ✅ NEW 

    def __str__(self):
        return f"{self.user.username} - {self.set.name} @ {self.started_at}"


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, null=True, blank=True)

    is_correct = models.BooleanField(null=True)       # ✅ True/False if answered, None if unanswered
    is_answered = models.BooleanField(default=False)  # ✅ explicitly track unanswered

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.question}"



# models.py
from django.db import models
# from django.contrib.auth.models import User

class Book(models.Model):
    subject = models.CharField(max_length=100)  # The subject this book relates to
    title = models.CharField(max_length=255, unique=True)  # Book title
    description = models.TextField(blank=True, null=True)  # Book description or summary
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # Price in USD
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)  # Rating out of 5
    source = models.CharField(max_length=255, blank=True, null=True)  # Optional: source of data, e.g., Gemini AI or API
    created_at = models.DateTimeField(auto_now_add=True)  # When the book entry was created
    updated_at = models.DateTimeField(auto_now=True)  # When it was last updated

    def __str__(self):
        return f"{self.title} ({self.subject})"


