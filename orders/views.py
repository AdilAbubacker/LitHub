import razorpay
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from cart.models import Cart, CartItem
from core import settings
from orders.models import Order, OrderItem
from promotions.models import Coupon, UsedCoupon
from store.models import BookVariant
from user_profile.models import Address


# Create your views here.
def order_placed(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()
    address = Address.objects.filter(user=request.user, is_default=True).first()
    order = Order.objects.create(
        user=request.user,
        address=address,
        payment_status='CASH_ON_DELIVERY',
        payment_method='CASH_ON_DELIVERY',
        order_status='PROCESSING',
        price=1
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            variant=item.variant,
            quantity=item.quantity,
            price=item.price
        )
        variant = BookVariant.objects.get(id=item.variant.id)
        variant.stock -= item.quantity
        variant.save()
        item.delete()

    try:
        coupon_code = request.session.get('coupon_code')
        coupon = Coupon.objects.get(code=coupon_code)
        if coupon.is_onetime_usable:
            used_coupon = UsedCoupon.objects.create(user=request.user, coupon=coupon)
            used_coupon.save()
        request.session['coupon_code'] = None
    except:
        pass

    return render(request, 'cart/order_placed.html')


def initiate_payment(request):
    if request.method == 'POST':
        # Retrieve the total price and other details from the backend
        cart = Cart.objects.get(user=request.user)
        items = CartItem.objects.filter(cart=cart)
        total_price = sum(item.price for item in items)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        payment = client.order.create({'amount': int(total_price * 100), 'currency': 'INR', 'payment_capture': 1})
        response_data = {
            'order_id': payment['id'],
            'amount': payment['amount'],
            'currency': payment['currency'],
            'key': settings.RAZORPAY_KEY_ID
        }
        return JsonResponse(response_data)

    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Invalid request method'})


def online_payment_order(request):
    if request.method == 'POST':
        payment_id = request.POST.getlist('payment_id')[0]
        orderid = request.POST.getlist('orderId')[0]
        signature = request.POST.getlist('signature')[0]
        user_address = Address.objects.filter(user=request.user, is_default=True).first()
        cart = Cart.objects.get(user_id=request.user)
        cart_items = cart.cartitem_set.all()
        total_price = cart.get_total_price()

        order = Order.objects.create(
            user=request.user,
            address=user_address,
            price=total_price,
            payment_status='PAID',
            payment_method='RAZORPAY',
            order_status='ORDERED',
            razor_pay_payment_id=payment_id,
            razor_pay_payment_signature=signature,
            razor_pay_order_id=orderid,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                price=item.price,
                quantity=item.quantity
            )

            variant = BookVariant.objects.get(id=item.variant.id)
            variant.stock -= item.quantity
            variant.save()
            item.delete()

        try:
            coupon_code = request.session.get('coupon_code')
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_onetime_usable:
                used_coupon = UsedCoupon.objects.create(user=request.user, coupon=coupon)
                used_coupon.save()
            request.session['coupon_code'] = None
        except:
            pass

        orderid = order.id

        return JsonResponse({'message': 'Order placed successfully', 'orderId': orderid})
    else:
        # Handle invalid request method (GET, etc.)
        return JsonResponse({'error': 'Invalid request method'})
