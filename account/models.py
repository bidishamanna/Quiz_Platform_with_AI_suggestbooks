from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Role constants
    STAFF = 'staff'
    STUDENT = 'student'

    ROLE_CHOICES = [
        (STAFF, 'Staff'),
        (STUDENT, 'Student'),
    ]

    # Override AbstractUser fields
    email = models.EmailField(unique=True)   # still unique, but not used for login
    username = models.CharField(max_length=150, unique=True)  # login handle

    # Custom field
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Use username to log in
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']   # when creating superuser, ask for email

    def __str__(self):
        return f"{self.username} ({self.role})"

from django.conf import settings
from django.db import models
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other')
        ],
        blank=True, null=True
    )
    dob = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    # Structured address fields
    village = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class UserToken(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='tokens')
    tokens = models.CharField(max_length=250,unique=True)    
    created_at = models.DateField(auto_now_add=True)
    expired_at = models.DateField()

    def __str__(self):
        return f"Token for {self.user.email}(Expires:{self.expired_at})"
    


