from django.contrib import admin
from questions.models import Question
from questions.models import Attempt
from questions.models import UserAnswer
# Register your models here.
admin.site.register(Question)
admin.site.register(Attempt)
admin.site.register(UserAnswer)

