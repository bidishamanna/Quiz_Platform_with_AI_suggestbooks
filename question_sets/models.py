import random
from django.db import models
from account.models import User
from category.models import Category

class Set(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delflag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ Add random 3-digit slug
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        unique_together = ("name", "category")

    def save(self, *args, **kwargs):
        if not self.slug:
            # generate until unique 3-digit slug is found
            while True:
                code = str(random.randint(100, 999))
                if not Set.objects.filter(slug=code).exists():
                    self.slug = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"
