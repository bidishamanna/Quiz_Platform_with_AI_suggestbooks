from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Book, CartItem
from account.decorators import jwt_required

 # Optional (depends on how you handle CSRF + JWT)

@csrf_exempt   # Optional (depends on how you handle CSRF + JWT)
@jwt_required
def add_to_cart(request, book_id):
    if request.method == "POST":
        user = request.user
        book = get_object_or_404(Book, id=book_id)

        # Add the selected book to the user's cart or increase the quantity
        cart_item, created = CartItem.objects.get_or_create(user=user, book=book)
        if not created:
            cart_item.quantity += 1
            cart_item.save()

        # Get the updated cart count for the user
        count = CartItem.objects.filter(user=user).count()

        return JsonResponse({'success': True, 'cart_count': count})

    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt   # Optional
@jwt_required
def update_cart(request, item_id):
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, id=item_id)
        action = request.POST.get("action")

        if action == "increase":
            cart_item.quantity += 1
        elif action == "decrease" and cart_item.quantity > 1:
            cart_item.quantity -= 1
        elif action == "remove":
            cart_item.delete()
            # Recalculate the total after removal
            cart_items = CartItem.objects.filter(user=request.user).select_related("book")
            total = sum(item.book.price * item.quantity for item in cart_items)
            count = cart_items.count()

            return JsonResponse({
                'success': True,
                'cart_count': count,
                'total': float(total),  # Recalculate the total
                'removed': True  # Flag to indicate the item was removed
            })

        cart_item.save()

        # Recalculate the total after update
        cart_items = CartItem.objects.filter(user=request.user).select_related("book")
        total = sum(item.book.price * item.quantity for item in cart_items)

        count = cart_items.count()

        return JsonResponse({
            'success': True,
            'cart_count': count,
            'total': float(total),  # Ensure total is returned as a float
            'quantity': cart_item.quantity,
            'total_item': float(cart_item.book.price * cart_item.quantity)
        })

    return JsonResponse({'error': 'Invalid method'}, status=405)

from django.shortcuts import render
from .models import CartItem
@jwt_required
def cart_detail(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user).select_related("book")

    data = [
        {
            "id": item.id,
            "title": item.book.title,
            "price": float(item.book.price),
            "quantity": item.quantity,
            "total": float(item.book.price * item.quantity),
        }
        for item in cart_items
    ]

    total = sum(item['total'] for item in data)

    # 👇 capture subject if passed in URL (?subject=Math)
    subject = request.GET.get("subject", "")

    return render(request, 'cart/cart_details.html', {
        'cart': data,
        'total': total,
        'last_subject': subject
    })

from django.views.decorators.http import require_POST
@jwt_required 

def checkout(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user).select_related("book")
    
    if not cart_items.exists():
        return render(request, 'cart/checkout.html', {
            'total': 0
        })
    
    total = sum(item.book.price * item.quantity for item in cart_items)

    return render(request, 'cart/checkout.html', {
        'total': total
    })

