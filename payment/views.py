# from django.shortcuts import render, get_object_or_404
# import razorpay
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST
# from django.conf import settings
# from django.contrib.auth.decorators import login_required
# from .models import Payment
# from subject.models import Subject

# from account.decorators import jwt_required, role_required  # adjust import if needed

# client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))  #Creates a Razorpay client object

# # # ✅ STUDENT: Can view payment page
# # @role_required('staff', 'student')
# # @login_required
# # def payment_view(request):
# #     subjects = Subject.objects.filter(delflag=False)  # Only active subjects
# #     return render(request, 'payment/payment.html', {'subjects': subjects})

# # New view using slug from the URL
# @role_required('staff', 'student')
# @login_required
# def payment_by_slug_view(request, slug):
#     subject = get_object_or_404(Subject, slug=slug, delflag=False)
#     return render(request, 'payment/payment.html', {'subject': subject})


# # ✅ STUDENT: Can create payment order

# @jwt_required
# @role_required('student')
# @require_POST
# def create_order(request):
#     subject_id = request.POST.get('subject_id')
#     subject = get_object_or_404(Subject, id=subject_id, delflag=False)

#     if subject.price == 0:
#         return JsonResponse({"error": "This subject is free. No payment required."})

#     amount = int(subject.price * 100)  # Razorpay expects amount in paise 

#     order_data = {  # all three parameters in your order_data are built-in Razorpay API fields:
#         "amount": amount,
#         "currency": "INR",
#         "payment_capture": 1, #payment_capture is a parameter provided by Razorpay’s API itself,if 1 then When the student pays, Razorpay will instantly deduct the money and mark payment as successful.
#     }

#     try:
#         razorpay_order = client.order.create(data=order_data) # this is create an order id  #Uses the client to create a new order in Razorpay.

#         Payment.objects.create(
#             user=request.user,
#             subject=subject,
#             amount=subject.price,
#             status='PENDING',
#             transaction_id=razorpay_order['id'] 
#         )

#         return JsonResponse({
#             'order_id': razorpay_order['id'], 
#             'key': settings.RAZORPAY_KEY_ID, # like saller or organiger account key , where the payment is added to track it
#             'amount': amount,
#             'subject': subject.name
#         })
#     except Exception as e:
#         return JsonResponse({"error": str(e)})

# # ✅ STUDENT: Can verify payment
# @csrf_exempt
# @jwt_required
# @role_required('student')
# @require_POST
# def verify_payment(request):
#     try:
#         data = request.POST
#         razorpay_order_id = data.get('razorpay_order_id')
#         razorpay_payment_id = data.get('razorpay_payment_id')
#         razorpay_signature = data.get('razorpay_signature')

#         if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
#             return JsonResponse({"error": "Missing payment details."})

#         client.utility.verify_payment_signature({
#             "razorpay_order_id": razorpay_order_id,
#             "razorpay_payment_id": razorpay_payment_id,
#             "razorpay_signature": razorpay_signature
#         })

#         payment = Payment.objects.get(transaction_id=razorpay_order_id)
#         payment.razorpay_payment_id = razorpay_payment_id 
#         payment.status = 'SUCCESS'
#         payment.save()

#         return JsonResponse({"success": True, "message": "Payment verified successfully."})
#     except razorpay.errors.SignatureVerificationError:
#         return JsonResponse({"error": "Payment verification failed."})
#     except Exception as e:
#         return JsonResponse({"error": str(e)})

# # ✅ STUDENT: Can view transaction history

# @login_required
# @role_required('staff', 'student')
# def transaction_history(request):
#     transactions = Payment.objects.filter(user=request.user).order_by('-timestamp')
    
#     return render(request, 'payment/transaction_history.html', {'transactions': transactions})



