import razorpay
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_control
from cart.models import Cart, CartItem
from core import settings
from orders.models import Order, OrderItem
from promotions.models import Coupon, UsedCoupon
from store.models import BookVariant
from user_profile.models import Address


# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='signin')
def order_placed(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()

    if cart_items:
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

        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_onetime_usable:
                used_coupon = UsedCoupon.objects.create(user=request.user, coupon=coupon)
                used_coupon.save()
            request.session['coupon_code'] = None

        order.order_status = 'ORDER CONFIRMED'

        return redirect('order_successful')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='signin')
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


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='signin')
def online_payment_order(request):
    if request.method == 'POST':
        payment_id = request.POST.getlist('payment_id')[0]
        order_id = request.POST.getlist('orderId')[0]
        signature = request.POST.getlist('signature')[0]
        user_address = Address.objects.filter(user=request.user, is_default=True).first()
        cart = Cart.objects.get(user_id=request.user)
        cart_items = cart.cartitem_set.all()
        total_price = cart.get_total_price()

        # Verify payment with Razorpay API
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            payment = client.payment.fetch(payment_id)
            if (
                    payment.get('status') == 'captured' and
                    payment.get('order_id') == order_id and
                    payment.get('amount') == total_price * 100  # Convert total_price to smallest currency unit
            ):
                order = Order.objects.create(
                    user=request.user,
                    address=user_address,
                    price=total_price,
                    payment_status='PAID',
                    payment_method='RAZORPAY',
                    order_status='ORDERED',
                    razor_pay_payment_id=payment_id,
                    razor_pay_payment_signature=signature,
                    razor_pay_order_id=order_id,
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

                coupon_code = request.session.get('coupon_code')
                if coupon_code:
                    coupon = Coupon.objects.get(code=coupon_code)
                    if coupon.is_onetime_usable:
                        used_coupon = UsedCoupon.objects.create(user=request.user, coupon=coupon)
                        used_coupon.save()
                    request.session['coupon_code'] = None
                return JsonResponse({'status': 'success', 'message': 'Payment verification successful'})
            else:
                # Payment verification failed
                return JsonResponse({'status': 'error', 'message': 'Payment verification failed'})
        except Exception as e:
            # Handle exceptions and errors
            return JsonResponse({'status': 'error', 'message': str(e)})

    else:
        # Handle invalid request method (GET, etc.)
        return JsonResponse({'error': 'Invalid request method'})


def order_successful(request):
    return render(request, 'cart/order_placed.html')


def order_pdf(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    context = {
        'order': order,
        'order_items': order_items
    }
    return render(request, 'orders/order_pdf.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='signin')
def cancel_order(request, order_id):
    # Retrieve the order or show a 404 page if the order does not exist
    order = get_object_or_404(Order, id=order_id)

    if order.payment_method == 'UPI' or order.payment_method == 'RAZORPAY':
        # Refund the payment through Razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        refund_response = client.payment.refund(order.razor_pay_payment_id, {'amount': int(order.price * 100)})

        # Refund successful
        if refund_response['status'] == 'processed':
            order.payment_status = 'REFUNDED'
            order.save()
            messages.success(request, "Order cancelled successfully. Refund processed to your source bank account.")
        else:
            messages.error(request, "Unable to process the refund to your source bank account. Please try again later.")
            return redirect('myorder_detail', order.id)

    # Update stock quantity
    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        variant = item.variant
        variant.stock += item.quantity
        variant.save()

    # Set the order status to 'CANCELLED'
    order.order_status = 'Cancelled'
    if order.payment_method == 'Cash on Delivery' or order.payment_method == 'CASH_ON_DELIVERY':
        order.payment_status = 'Cancelled'
        messages.success(request, "Order cancelled successfully. There won't be any refund as you've opted 'Cash on "
                                  "Delivery' as the payment method.")
    order.save()

    return redirect('myorder_detail', order.id)


@login_required(login_url='signin')
def request_return(request, order_id):
    # Retrieve the order or show a 404 page if the order does not exist
    order = get_object_or_404(Order, id=order_id)

    order.order_status = 'Return Requested'
    order.save()

    messages.success(request, "Your request for return has been sent successfully. Refund will be initiated once we "
                              "reviewd your order.")

    return redirect('myorder_detail', order.id)

