from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Question(models.Model):
    text = models.TextField(verbose_name="Question Text")
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)

    correct_option = models.PositiveSmallIntegerField(choices=[
        (1, "Option 1"),
        (2, "Option 2"),
        (3, "Option 3"),
        (4, "Option 4"),
    ])

    def __str__(self):
        return self.text


class UserAnswer(models.Model):
  
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.PositiveSmallIntegerField()
    is_correct = models.BooleanField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - Q{self.question.id} - Option {self.selected_option}"

    

