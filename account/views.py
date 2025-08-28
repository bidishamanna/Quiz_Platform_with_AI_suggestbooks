from django.shortcuts import render
from Online_Test.settings import EMAIL_HOST_USER
from account.models import User
from django.http import JsonResponse, HttpResponseBadRequest
import json  
from datetime import datetime, date
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import re
from django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from category.models import Category
User = get_user_model()
from account.authentication import create_access_token, create_refresh_token
from django.views.decorators.http import require_GET
from account.models import User, UserToken
from account.decorators import jwt_required,role_required
from django.urls import reverse
# Create your views here.

def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode() 
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        return redirect('/account/login_view/?activated=true')
    else:
        return redirect('/account/login_view/?invalid_token=true')
    

def send_verification_email(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL 
    current_site = get_current_site(request)            # Get the current site
    message = render_to_string(email_template, {        # Render the email template with the context
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),     # Encode the user's primary key
        'token': default_token_generator.make_token(user),      # Generate a token for the user
    })
    to_email = user.email
    mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
    mail.content_subtype = "html"
    mail.send()
   



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

@require_POST
@csrf_exempt  # OR handle CSRF token properly if using from browser
def check_email_unique(request):
    """
    AJAX POST endpoint to check if an email is already taken.
    """
    email = request.POST.get('email', '').strip()

    if not email:
        return JsonResponse({'exists': False, 'error': 'Email is required.'}, status=400)

    exists = User.objects.filter(email__iexact=email).exists()
    return JsonResponse({'exists': exists})



import re
from datetime import datetime, date
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from .models import User


import re
from datetime import datetime, date
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.conf import settings
from .models import User, Profile
# from .utils import send_verification_email   # assuming you already have this

# Regex patterns
# NAME_REGEX = r'^[A-Za-z]{2,30}$'
USERNAME_REGEX = r'^[A-Za-z0-9_]{4,20}$'
EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
# DOB_REGEX = r'^(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$'

# GENDER_OPTIONS = ['Male', 'Female', 'Other']

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth import get_user_model
import re

User = get_user_model()
import re
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth import get_user_model


User = get_user_model()

USERNAME_REGEX = r'^[A-Za-z0-9_]{4,20}$'
EMAIL_REGEX = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'


def registration(request):
    if request.method == 'GET':
        role_param = request.GET.get('role', 'student')
        if role_param in ['staff', 'student']:
            return render(
                request,
                f'account/{role_param}_register.html',
                {'roles': User.ROLE_CHOICES}
            )
        return HttpResponseBadRequest("Invalid role in URL")

    elif request.method == 'POST':
        errors = {}

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        role = request.POST.get("role", "").strip()

        # ================= VALIDATIONS =================
        # Username
        if not username or not re.match(USERNAME_REGEX, username):
            errors['username'] = "Username must be 4–20 chars (letters, numbers, underscores)."
        elif User.objects.filter(username__iexact=username).exists():
            errors['username'] = "Username already exists."

        # Email
        if not email or not re.match(EMAIL_REGEX, email):
            errors['email'] = "Invalid email address."
        elif User.objects.filter(email__iexact=email).exists():
            errors['email'] = "Email already exists."

        # Password
        if not password or not re.match(PASSWORD_REGEX, password):
            errors['password'] = (
                "Password must be 8+ chars and include uppercase, lowercase, "
                "number, and special character."
            )

        # Confirm Password
        if not confirm_password or confirm_password != password:
            errors['confirm_password'] = "Passwords do not match."

        # Role
        if role not in dict(User.ROLE_CHOICES):
            errors['role'] = "Invalid role."

        # If errors → return
        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # ================= CREATE USER =================
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            is_active=False
        )

        # ================= SEND EMAIL =================
        send_verification_email(
            request,
            user,
            'Please activate your account',
            'account/email/account_verification_email.html'
        )

        return JsonResponse({
            'success': True,
            'message': 'Check your email for the activation link!',
            'redirect_url': '/account/login_view/'
        }, status=200)



    return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

def login_view(request):
    if request.method == 'GET':
        return render(request, 'account/login.html')

    elif request.method == 'POST':
        try:
            username = request.POST.get("username")   # 👈 use username instead of email
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)  # 👈 fixed
            if user is None:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=401)
            if not user.is_active:
                return JsonResponse({'status': 'error','message': 'Your account is not activated. Please check your email.'}, status=403)

            login(request, user)
            access_token = create_access_token(user)
            refresh_token = create_refresh_token(user)

            # Redirect based on role
            if user.role == 'staff':
                redirect_url = '/account/staff_dashboard/'
            elif user.role == 'student':
                redirect_url = reverse('home')
            else:
                redirect_url = '/'

            # Save refresh token in DB
            UserToken.objects.create(
                user=user,
                tokens=refresh_token,
                expired_at=timezone.now() + timedelta(days=7)
            )

            response = JsonResponse({
                "status": "success",
                "redirect_url": redirect_url
            })

            # Set access token (short-lived)
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=False,   # 👉 set True in production
                samesite='Lax',
                max_age=2400,  # 40 min
                path='/'
            )

            # Set refresh token (long-lived)
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=7 * 24 * 60 * 60,  # 7 days
                path="/"
            )

            return response
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method'}, status=405)

   
from django.http import JsonResponse

# def check_login_status(request):
#     return JsonResponse({'is_login': request.user.is_authenticated})



# @login_required
# def staff_dashboard(request):
#     if not request.user.is_staff_member():
#         return JsonResponse("Only staff members can access this page.")
#     if request.method != 'GET':
#         return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

#     return render(request, 'account/staff_dashboard.html', {'user': request.user})


from django.shortcuts import render, get_object_or_404
from .models import Profile

def my_profile(request):
    # Fetch the profile for the logged-in user
    profile = get_object_or_404(Profile, user=request.user)
    
    return render(request, 'account/my_profile.html', {'profile': profile})



# account/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib import messages
import re
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
import re
from datetime import datetime, date

GENDER_OPTIONS = ['Male', 'Female', 'Other']
NAME_REGEX = r'^[A-Za-z]{2,30}$'
PHONE_REGEX = r'^\+?\d{10,15}$'
@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        gender = request.POST.get('gender', '').strip()
        dob_str = request.POST.get('dob', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Structured address fields
        village = request.POST.get('village', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()

        errors = {}

        # Validate first name
        if first_name and not re.match(NAME_REGEX, first_name):
            errors['first_name'] = "Only letters allowed (2–30 chars)."
        # Validate last name
        if last_name and not re.match(NAME_REGEX, last_name):
            errors['last_name'] = "Only letters allowed (2–30 chars)."
        # Gender
        if gender not in GENDER_OPTIONS:
            errors['gender'] = "Select a valid gender."
        # DOB
        if dob_str:
            try:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                if dob > today:
                    errors['dob'] = "DOB cannot be in the future."
                elif age < 10:
                    errors['dob'] = "You must be at least 10 years old."
            except ValueError:
                errors['dob'] = "Invalid date format."
        else:
            dob = None
        # Phone
        if phone and not re.match(PHONE_REGEX, phone):
            errors['phone'] = "Invalid phone number."

        if errors:
            return render(request, 'account/edit_profile.html', {
                'profile': profile,
                'errors': errors,
                'gender_options': GENDER_OPTIONS
            })

        # Update profile
        profile.first_name = first_name
        profile.last_name = last_name
        profile.gender = gender
        profile.dob = dob
        profile.phone = phone
        
        # Update structured address
        profile.village = village
        profile.city = city
        profile.state = state
        profile.postal_code = postal_code

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('my_profile')

    return render(request, 'account/edit_profile.html', {
        'profile': profile,
        'gender_options': GENDER_OPTIONS
    })



@jwt_required
@role_required('student')  # directly using 'student' as string
def student_dashboard(request):
    categories = Category.objects.filter(delflag=False)

    if request.method == "POST":
        selected_category_id = request.POST.get("category")
        if selected_category_id:
            return redirect("start_test", category_id=selected_category_id)

    context = {
        'user': request.user,
        'categories': categories,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "account/student_dashboard.html", context)
    else:
        return render(request, "account/student_dashboard.html", context)    





@jwt_required
@role_required('staff')  # directly using 'staff' as string
def staff_dashboard(request):
    context = {
        'user': request.user,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "account/staff_dashboard.html", context)
    else:
        return render(request, "account/staff_dashboard.html", context)


def logout_view(request):
    try:
        user = request.user
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token:
            UserToken.objects.filter(user=user, tokens=refresh_token).delete()

        logout(request)

        response = redirect('login_view')

        # Delete cookies with the correct paths
        response.delete_cookie('access_token', path='/')             # Access token
        response.delete_cookie('refresh_token', path='/')    # Refresh token

        return response

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
# forget password

# from django.core.mail import send_mail
# from django.http import HttpResponse

# def forget_password(request): 
#     if request.method == 'POST':
#         email = request.POST.get("email")
#         if User.objects.filter(email=email).exists():
#             user = User.objects.get(email=email)
#             print('user exist')
#             send_mail("Reset your password:",f"current user : {user} ! To reset password click on given link \n  http://127.0.0.1:8000/newpassword/{user}/",EMAIL_HOST_USER,[email],fail_silently=True)
#             return HttpResponse('link send to your model')
#         return render(request,'account/email/forget_password.html')   
#     return render(request,'account/email/forget_password.html')  


# def newpassword(request,email):
#     userid = User.objects.get(email=email)
#     if request.method == 'POST':
#         pass1 = request.POST.get("password1")
#         pass2 = request.POST.get("password2")
#         if pass1 == pass2:
#             userid.set_password(pass1)
#             userid.save()
#             return HttpResponse('password reset')

#     return render(request,'account/email/reset_password.html')    
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from account.models import User
from urllib.parse import quote, unquote
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from urllib.parse import quote
from django.conf import settings

from django.core.mail import send_mail
from urllib.parse import quote
from django.conf import settings
from django.http import JsonResponse


def forget_password(request): 
    if request.method == 'POST':
        email = request.POST.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            email_encoded = quote(email)
            reset_link = f"http://127.0.0.1:8000/account/newpassword/{email_encoded}/"

            send_mail(
                "Reset your password:",
                f"Click this link to reset: {reset_link}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
            return JsonResponse({"success": True, "message": "Reset link sent to your email."})

        else:
            return JsonResponse({"success": False, "message": "Email not found."})
    
    return render(request,'account/email/forget_password.html')


PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

from urllib.parse import unquote
import re
# from django.contrib.auth.models import User
from django.shortcuts import render, redirect

PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

def newpassword(request, email):
    email = unquote(email)
    user = User.objects.get(email=email)
    context = {}

    if request.method == 'POST':
        pass1 = request.POST.get("password1")
        pass2 = request.POST.get("password2")

        if pass1 != pass2:
            context['password2_error'] = "Passwords do not match."
        elif not re.match(PASSWORD_REGEX, pass1):
            context['password1_error'] = (
                "Password must be at least 8 characters long, contain an uppercase letter, "
                "a lowercase letter, a number, and a special character."
            )
        else:
            user.set_password(pass1)
            user.save()
            context['success'] = True
            context['message'] = "Password has been reset successfully."

    return render(request, 'account/email/reset_password.html', context)



