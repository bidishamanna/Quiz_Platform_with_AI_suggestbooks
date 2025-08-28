# from django.db import models

# # Create your models here.
# from django.db import models
# from account.models import User
# from subject.models import Subject  # If your paid item is a Subject

# class Payment(models.Model):
#     STATUS_CHOICES = [
#         ('PENDING', 'Pending'),
#         ('SUCCESS', 'Success'),
#         ('FAILED', 'Failed'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="payments")
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
#     transaction_id = models.CharField(max_length=100, unique=True)
#     razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.subject.name} - {self.status}"



# # models.py
# from django.db import models
# from django.contrib.auth.models import User

# class Payment(models.Model):
#     STATUS_CHOICES = [
#         ('PENDING', 'Pending'),
#         ('SUCCESS', 'Success'),
#         ('FAILED', 'Failed'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
#     book = models.ForeignKey("Book", on_delete=models.CASCADE, related_name="payments")
#     amount = models.DecimalField(max_digits=10, decimal_places=2)  # INR price
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
#     transaction_id = models.CharField(max_length=100, unique=True)
#     razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.book.title} - {self.status}"

