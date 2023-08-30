from django.db.models import Sum, Count
from django.shortcuts import render
from cart.models import Wishlist, CartItem, WishlistItem, Wallet
from orders.models import Order
from user_profile.models import Address


# Create your views here.
def user_profile(request):
    address = Address.objects.filter(is_default=True).first()
    cart_count = CartItem.objects.filter(
        cart__user=request.user.id).aggregate(Sum('quantity'))['quantity__sum']
    wishlist_count = WishlistItem.objects.filter(
        wishlist__user=request.user.id).aggregate(Count('variant'))['variant__count']

    context = {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'address': address,
    }
    return render(request, 'user_profile/user_profile.html', context)


def address_management(request):
    addresses = Address.objects.filter(user__id=request.user.id).order_by('-is_default', 'id')
    cart_count = CartItem.objects.filter(
        cart__user=request.user.id).aggregate(Sum('quantity'))['quantity__sum']
    wishlist_count = WishlistItem.objects.filter(
        wishlist__user=request.user.id).aggregate(Count('variant'))['variant__count']

    context = {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'addresses': addresses,
    }
    return render(request, 'user_profile/address_management.html', context)


def set_as_default(request, address_id):
    address = Address.objects.get(id=address_id)
    old_default = Address.objects.filter(is_default=True)
    for old in old_default:
        old.is_default = False
        old.save()
    address.is_default = True
    address.save()
    addresses = Address.objects.filter(user__id=request.user.id).order_by('-is_default', 'id')
    return render(request, 'user_profile/address_management.html', {'addresses': addresses})


def delete_address(request, address_id):
    current_address = Address.objects.get(id=address_id)
    if current_address.is_default:
        new_address = Address.objects.exclude(id=address_id).first()
        new_address.is_default = True
        new_address.save()
    current_address.is_active = False
    current_address.save()
    addresses = Address.objects.filter(user__id=request.user.id).order_by('-is_default', 'id')
    return render(request, 'user_profile/address_management.html', {'addresses': addresses})


def add_address(request):
    cart_count = CartItem.objects.filter(
        cart__user=request.user.id).aggregate(Sum('quantity'))['quantity__sum']
    wishlist_count = WishlistItem.objects.filter(
        wishlist__user=request.user.id).aggregate(Count('variant'))['variant__count']

    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        pincode = request.POST.get('pincode')
        address = request.POST.get('address')
        landmark = request.POST.get('landmark')
        city = request.POST.get('city')
        district = request.POST.get('district')
        state = request.POST.get('state')

        address = Address(
            user=request.user,
            name=name,
            mobile=mobile,
            pincode=pincode,
            address=address,
            landmark=landmark,
            city=city,
            district=district,
            state=state,
        )
        address.save()

        addresses = Address.objects.filter(user__id=request.user.id).order_by('-is_default', 'id')
        context = {
            'cart_count': cart_count,
            'wishlist_count': wishlist_count,
            'addresses': addresses,
        }
        return render(request, 'user_profile/address_management.html', context)

    context = {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
    }

    return render(request, 'user_profile/add_address.html', context)


def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    cart_count = CartItem.objects.filter(
        cart__user=request.user.id).aggregate(Sum('quantity'))['quantity__sum']
    wishlist_count = WishlistItem.objects.filter(
        wishlist__user=request.user.id).aggregate(Count('variant'))['variant__count']

    context = {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'orders': orders
    }
    return render(request, 'user_profile/myorders.html', context)


def myorder_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = order.orderitem_set.all()
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'user_profile/myorder_detail1.html', context)


def my_wishlist(request):
    wishlist = Wishlist.objects.get(user=request.user.id)
    wishlist_items = wishlist.wishlistitem_set.all()
    cart_count = CartItem.objects.filter(
        cart__user=request.user.id).aggregate(Sum('quantity'))['quantity__sum']
    wishlist_count = WishlistItem.objects.filter(
        wishlist__user=request.user.id).aggregate(Count('variant'))['variant__count']

    context = {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'wishlist_items': wishlist_items
    }
    return render(request, 'user_profile/profile_wishlist.html', context)


def my_wallet(request):
    wallet = Wallet.objects.get(user=request.user.id)
    balance = wallet.balance
    cart_count = CartItem.objects.filter(
        cart__user=request.user.id).aggregate(Sum('quantity'))['quantity__sum']
    wishlist_count = WishlistItem.objects.filter(
        wishlist__user=request.user.id).aggregate(Count('variant'))['variant__count']

    context = {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'balance': balance
    }
    return render(request, 'user_profile/wallet.html', context)