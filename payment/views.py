from django.shortcuts import render, get_object_or_404
import razorpay
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Payment
from subject.models import Subject

from account.decorators import jwt_required, role_required  # adjust import if needed

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))  #Creates a Razorpay client object

# # ✅ STUDENT: Can view payment page
# @role_required('staff', 'student')
# @login_required
# def payment_view(request):
#     subjects = Subject.objects.filter(delflag=False)  # Only active subjects
#     return render(request, 'payment/payment.html', {'subjects': subjects})

# # New view using slug from the URL
# @role_required('staff', 'student')
# @login_required
# def payment_by_slug_view(request, slug):
#     subject = get_object_or_404(Subject, slug=slug, delflag=False)
#     return render(request, 'payment/payment.html', {'subject': subject})

# from accounts.decorators import jwt_required, role_required  # adjust import

# Razorpay client
# client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from questions.models import Book
from payment.models import Payment
# from myapp.decorators import jwt_required, role_required  # your decorators

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
from cart.models import CartItem  # make sure to import your model

@jwt_required
@role_required('student')
@require_POST
def create_order(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user).select_related("book")

    if not cart_items.exists():
        return JsonResponse({"error": "Cart is empty"}, status=400)

    total_amount = sum(item.book.price * item.quantity for item in cart_items)
    if total_amount <= 0:
        return JsonResponse({"error": "Cart total is zero"}, status=400)

    amount_paise = int(total_amount * 100)

    order_data = {
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1,
    }

    try:
        razorpay_order = client.order.create(data=order_data)

        payment = Payment.objects.create(
            user=request.user,
            amount=total_amount,
            status='PENDING',
            transaction_id=razorpay_order['id']
        )

        # Save related books
        payment.books.set([item.book for item in cart_items])

        return JsonResponse({
            'order_id': razorpay_order['id'],
            'key': settings.RAZORPAY_KEY_ID,
            'amount': amount_paise,
            'books': [item.book.title for item in cart_items],
            'total': float(total_amount)
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Payment
from .utils import send_invoice_pdf   # ✅ import the function we created earlier
@csrf_exempt
@jwt_required
@role_required('student')
@require_POST
def verify_payment(request):
    try:
        data = request.POST
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        # Verify signature
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })

        # Get Payment
        payment = get_object_or_404(Payment, transaction_id=razorpay_order_id)
        payment.razorpay_payment_id = razorpay_payment_id
        payment.status = 'SUCCESS'
        payment.save()

        # ✅ Clear cart after payment
        request.session['cart'] = []

        # ✅ Send Invoice Email with PDF
        books = payment.books.all()
        total = payment.amount
        user = payment.user
        send_invoice_pdf(user, books, total, razorpay_order_id, payment.timestamp)

        return JsonResponse({"success": True, "message": "Payment verified successfully. Invoice sent to email."})

    except Exception as e:
        return JsonResponse({"error": str(e)})


# ✅ STUDENT: Can view transaction history
@login_required
@role_required('staff', 'student')
def transaction_history(request):
    transactions = Payment.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'payment/transaction_history.html', {'transactions': transactions})

