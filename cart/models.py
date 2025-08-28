from django.db import models

# Create your models here.
# models.py
from django.db import models
from account.models import User
from questions.models import Book
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')  # prevent duplicates

    def __str__(self):
        return f"{self.book.title} x {self.quantity} ({self.user.username})"

