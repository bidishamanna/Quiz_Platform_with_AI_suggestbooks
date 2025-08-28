from django.db import models

# Create your models here.
from django.db import models
from category.models import Category
from account.models import User 

    

# -------------------------------
class Subject(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subjects")
    delflag = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    



    