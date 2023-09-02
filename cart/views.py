from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.shortcuts import render, redirect
from cart.models import Cart, CartItem, Wishlist, WishlistItem
from promotions.models import Coupon, UsedCoupon
from store.models import BookVariant
import razorpay

from user_profile.models import Address


# Create your views here.
@login_required(login_url='signin')
def cart_summary(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all().order_by('variant')
    total_price = cart.cartitem_set.aggregate(total=Sum('price'))['total'] if cart else 0
    wishlist_count = WishlistItem.objects.filter(wishlist__user=request.user.id).aggregate(Count('variant'))['variant__count']
    cart_count = (CartItem.objects.filter(cart__user=request.user.id).aggregate(Sum('quantity'))['quantity__sum'])
    insufficient_stock = None
    for item in cart_items:
        if item.variant.stock <= 0:
            insufficient_stock = 1

    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        coupon = Coupon.objects.get(code=coupon_code)
        if coupon.discount_type == 'percentage':
            total_discount = total_price * (coupon.discount_value / 100)
            coupon_discount = min(total_discount, coupon.min_or_max_amount)
        else:
            coupon_discount = coupon.discount_value
    else:
        coupon_discount = 0

    shipping_charge = 40
    try:
        total_amount = total_price + shipping_charge - coupon_discount
    except:
        return render(request, 'cart/empty_cart.html')

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
        'coupon_discount': coupon_discount,
        'shipping_charge': shipping_charge,
        'total_amount': total_amount,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'insufficient_stock': insufficient_stock
    }
    return render(request, 'cart/cart.html', context)


@login_required(login_url='signin')
def add_to_cart(request, variant_id):
    variant = BookVariant.objects.get(id=variant_id)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user)

    cart_item, created = cart.cartitem_set.get_or_create(variant=variant)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect('product_details', variant.slug)


def update_quantity(request, cart_item_id, num):
    cart_item = CartItem.objects.get(id=cart_item_id)
    if num == 1 and cart_item.variant.stock > cart_item.quantity:
        cart_item.quantity += 1
    elif num == 0 and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    return redirect('cart_summary')


def remove_cart_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.delete()
    return redirect('cart_summary')


@login_required(login_url='signin')
def wishlist_summary(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.wishlistitem_set.all().order_by('variant')
    wishlist_count = WishlistItem.objects.filter(wishlist__user=request.user.id).aggregate(Count('variant'))['variant__count']
    cart_count = CartItem.objects.filter(
        cart__user=request.user.id).aggregate(Sum('quantity'))['quantity__sum']

    context = {
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
    }
    return render(request, 'cart/wishlist.html', context)
    # except:
    #     return render(request, 'cart/empty_wishlist.html')


@login_required(login_url='signin')
def add_to_wishlist(request, variant_id):
    variant = BookVariant.objects.get(id=variant_id)
    user = request.user
    wishlist, created = Wishlist.objects.get_or_create(user=user)

    try:
        wishlist_item = WishlistItem.objects.get(wishlist=wishlist, variant=variant)
    except:
        wishlist_item = WishlistItem.objects.create(wishlist=wishlist, variant=variant)
    wishlist_item.save()

    return redirect('product_details', variant.slug)


def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = WishlistItem.objects.get(id=wishlist_item_id)
    wishlist_item.delete()

    return redirect('wishlist_summary')


def wishlist_to_cart(request, wishlist_item_id):
    wishlist_item = WishlistItem.objects.get(id=wishlist_item_id)
    variant = wishlist_item.variant
    wishlist_item.delete()
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = cart.cartitem_set.get_or_create(variant=variant)

    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect('wishlist_summary')


def checkout(request):
    cart = Cart.objects.get(user=request.user)
    addresses = Address.objects.filter(user__id=request.user.id).order_by('-is_default', 'id')
    cart_items = cart.cartitem_set.all()
    total_price = cart.cartitem_set.aggregate(total=Sum('price'))['total'] if cart else 0

    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        coupon = Coupon.objects.get(code=coupon_code)
        if coupon.discount_type == 'percentage':
            total_discount = total_price * (coupon.discount_value / 100)
            coupon_discount = min(total_discount, coupon.min_or_max_amount)
        else:
            coupon_discount = min(coupon.discount_value, coupon.min_or_max_amount)

    else:
        coupon_discount = 0

    shipping_charge = 40
    total_amount = total_price + shipping_charge - coupon_discount

    context = {
        'cart_items': cart_items,
        'addresses': addresses,
        'total_price': total_price,
        'coupon_discount': coupon_discount,
        'shipping_charge': shipping_charge,
        'total_amount': total_amount,
    }
    return render(request, 'cart/checkout.html', context)
