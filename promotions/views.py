from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import render, redirect

from cart.models import Cart
from .models import Coupon, UsedCoupon


# Create your views here.
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        cart = Cart.objects.get(user=request.user)
        total_price = cart.cartitem_set.aggregate(total=Sum('price'))['total'] if cart else 0
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_onetime_usable and UsedCoupon.objects.filter(user=request.user, coupon=coupon).exists():
                messages.warning(request, 'Sorry, this coupon is already used.')
            elif coupon.discount_type == 'fixed' and total_price < coupon.min_or_max_amount:
                messages.warning(request, 'Cart price should be more than **.')
            else:
                request.session['coupon_code'] = coupon.code
                messages.success(request, 'Coupon applied successfully.')
                return redirect('cart_summary')
        except:
            messages.warning(request, 'Enter a valid coupon code.')
    return redirect('cart_summary')


