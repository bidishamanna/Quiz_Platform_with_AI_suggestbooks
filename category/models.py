import random
from django.db import models
from account.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    delflag = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a random 4-digit number
            rand_num = random.randint(1000, 9999)
            base_slug = slugify(self.name)
            new_slug = f"{rand_num}-{base_slug}"

            # Ensure uniqueness
            while Category.objects.filter(slug=new_slug).exists():
                rand_num = random.randint(1000, 9999)
                new_slug = f"{rand_num}-{base_slug}"

            self.slug = new_slug

        super().save(*args, **kwargs)
