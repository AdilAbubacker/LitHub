from datetime import timedelta, datetime

import json

from _decimal import Decimal
from django.db import models
from django.http import JsonResponse
from django.db.models import Count
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from orders.models import Order, OrderItem
from promotions.models import Coupon
from store.models import Category, Book, BookVariant, Author, Publisher


# Create your views here.
def admin_home(request):
    if request.user.is_superuser:
        return render(request, 'adminpanel/admin_base.html')
    return redirect('home')


def category_list(request):
    if request.user.is_superuser:
        search = request.GET.get('search')

        if search:
            search = request.GET.get('search')
            categoies = Category.objects.filter(name__icontains=search)
        else:
            categoies = Category.objects.all().order_by('name')

        paginator = Paginator(categoies, 5)
        page = request.GET.get('page')
        categoies = paginator.get_page(page)
        return render(request, 'adminpanel/admin_category_list.html', {'categoies': categoies})
    return redirect('home')



def create_category(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST['name']
            description = request.POST.get('description', '')
            image = request.FILES.get('image')

            category = Category(name=name, description=description, image=image)
            category.save()

            return redirect('admin-category_list')

        return render(request, 'adminpanel/admin_add_category.html')


def enable_category(request, category_id):
    if request.user.is_superuser:
        category = Category.objects.get(slug=category_id)
        category.is_active = True
        category.save()
        return redirect('admin-category_list')


def disable_category(request, category_id):
    if request.user.is_superuser:
        category = Category.objects.get(id=category_id)
        category.is_active = False
        category.save()
        return redirect('admin-category_list')


def delete_category(request, category_id):
    if request.user.is_superuser:
        category = Category.objects.get(id=category_id)
        category.delete()
        return redirect('admin-category_list')


def edit_category(request, category_id):
    if request.user.is_superuser:
        category = Category.objects.get(id=category_id)
        if request.method == 'POST':
            name = request.POST['name']
            description = request.POST.get('description', '')
            image = request.FILES.get('image')
            offer_percentage = request.POST.get('offer_percentage', '')

            category.name = name
            category.description = description
            category.offer_percentage = offer_percentage
            if image:
                category.image = image
            category.save()

            return redirect('admin-category_list')

        return render(request, 'adminpanel/edit_category.html', {'category': category})


def users_list(request):
    if request.user.is_superuser:
        search = request.GET.get('search')

        if search:
            users = User.objects.filter(username__icontains=search)
        else:
            users = User.objects.all().order_by('id')

        paginator = Paginator(users, 7)
        page = request.GET.get('page')
        users = paginator.get_page(page)

        return render(request, 'adminpanel/users_list.html', {'users': users})


def block_user(request, user_id):
    if request.user.is_superuser:
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save()
        return redirect('admin-users_list')


def unblock_user(request, user_id):
    if request.user.is_superuser:
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        return redirect('admin-users_list')


def delete_user(request, user_id):
    if request.user.is_superuser:
        user = User.objects.get(id=user_id)
        user.delete()
        return redirect('admin-users_list')


def products_list(request):
    if request.user.is_superuser:
        search = request.GET.get('search')

        if search:
            books = Book.ofilter(name__icontains=search)
        else:
            books = Book.objects.all()

        paginator = Paginator(books, 5)
        page = request.GET.get('page')
        books = paginator.get_page(page)
        return render(request, 'adminpanel/admin_product_list.html', {'books': books})


def edit_product(request, book_id):
    if request.user.is_superuser:
        book = Book.objects.get(id=book_id)
        if request.method == 'POST':
            book.name = request.POST['name']
            book.title = request.POST['title']
            category_id = request.POST.get('categorySelect')
            book.category = get_object_or_404(Category, pk=category_id)
            author_id = request.POST.get('authorSelect')
            book.author = get_object_or_404(Author, pk=author_id)
            publisher_id = request.POST.get('publisherSelect')
            book.publisher = get_object_or_404(Publisher, pk=publisher_id)
            book.no_of_pages = request.POST.get('pagenum')
            book.description = request.POST.get('description', '')
            cover_image = request.FILES.get('image')
            book.offer_percentage = request.POST.get('offer_percentage', '')

            if cover_image:
                book.cover_image = cover_image

            book.save()
            return redirect('admin-products_list')

        categories = Category.objects.all()
        authors = Author.objects.all()
        publishers = Publisher.objects.all()
        context = {
            'categories': categories,
            'authors': authors,
            'publishers': publishers,
            'book': book,
        }
        return render(request, 'adminpanel/edit_product.html', context)


def add_product(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST['name']
            title = request.POST['title']
            category_id = request.POST.get('categorySelect')
            category = get_object_or_404(Category, pk=category_id)
            author_id = request.POST.get('authorSelect')
            author = get_object_or_404(Author, pk=author_id)
            publisher_id = request.POST.get('publisherSelect')
            publisher = get_object_or_404(Publisher, pk=publisher_id)
            no_of_pages = request.POST.get('pagenum')
            description = request.POST.get('description', '')
            image = request.FILES.get('image')

            book = Book(name=name, title=title, category=category, author=author, publisher=publisher,
                        no_of_pages=no_of_pages, description=description, cover_image=image)
            book.save()

            return redirect('admin-products_list')

        categories = Category.objects.all()
        authors = Author.objects.all()
        publishers = Publisher.objects.all()
        context = {
            'categories': categories,
            'authors': authors,
            'publishers': publishers,
        }
        return render(request, 'adminpanel/add_product.html', context)


def process_image(request):
    if request.user.is_superuser:
        book = get_object_or_404(Book, id=book_id)

        if request.method == 'POST':
            image = request.FILES.get('image')
            if image:
                book.image = image
                book.save()
                return JsonResponse({'message': 'Image processed successfully'})
            else:
                return JsonResponse({'error': 'No image data found'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)


def enable_product(request, book_id):
    if request.user.is_superuser:
        book = Book.objects.get(id=book_id)
        book.is_active = True
        book.save()
        return redirect('admin-products_list')


def disable_product(request, book_id):
    if request.user.is_superuser:
        book = Book.objects.get(id=book_id)
        book.is_active = False
        book.save()
        return redirect('admin-products_list')


def view_product_variants(request, book_id):
    if request.user.is_superuser:
        book = Book.objects.get(id=book_id)
        variants = book.bookvariant_set.all()

        paginator = Paginator(variants, 5)
        page = request.GET.get('page')
        variants = paginator.get_page(page)
        return render(request, 'adminpanel/view_product_variants.html', {'variants': variants, 'book_id': book_id})


def edit_variant(request, variant_id, book_id):
    if request.user.is_superuser:
        return render(request, 'adminpanel/edit_product.html')


def enable_variant(request, variant_id, book_id):
    if request.user.is_superuser:
        variant = BookVariant.objects.get(id=variant_id)
        variant.is_active = True
        variant.save()
        return redirect('view_product_variants', book_id)


def disable_variant(request, variant_id, book_id):
    if request.user.is_superuser:
        variant = BookVariant.objects.get(id=variant_id)
        variant.is_active = False
        variant.save()
        return redirect('view_product_variants', book_id)


def add_variant(request, book_id):
    # if request.method == 'POST':
    #     name = request.POST['name']
    #     title = request.POST['title']
    #     category_id = request.POST.get('categorySelect')
    #     category = get_object_or_404(Category, pk=category_id)
    #     author_id = request.POST.get('authorSelect')
    #     author = get_object_or_404(Author, pk=author_id)
    #     publisher_id = request.POST.get('publisherSelect')
    #     publisher = get_object_or_404(Publisher, pk=publisher_id)
    #     no_of_pages = request.POST.get('pagenum')
    #     description = request.POST.get('description', '')
    #     image = request.FILES.get('image')
    #
    #     book = Book(name=name, title=title, category=category, author=author, publisher=publisher,
    #                 no_of_pages=no_of_pages, description=description, cover_image=image)
    #     book.save()
    #
    #     return redirect('admin-products_list')

    # categories = Category.objects.all()
    # authors = Author.objects.all()
    # publishers = Publisher.objects.all()
    # context = {
    #     'categories': categories,
    #     'authors': authors,
    #     'publishers': publishers,
    # }
    return render(request, 'adminpanel/add_variant.html')


def orders_list(request):
    if request.user.is_superuser:
        orders = Order.objects.all().order_by('-id')
        context = {
            'orders': orders,
        }
        return render(request, 'adminpanel/orders_list.html', context)


def admin_order_details(request, order_id):
    if request.user.is_superuser:
        order = Order.objects.get(id=order_id)
        order_items = order.orderitem_set.all()
        context = {
            'order': order,
            'order_items': order_items,
        }
        return render(request, 'adminpanel/admin_order_details.html', context)


def change_order_status(request, order_id, status):
    if request.user.is_superuser:
        order = Order.objects.get(id=order_id)
        order.order_status = status
        order.save()
        return redirect('admin_order_details', order.id)


def coupon_management(request):
    if request.user.is_superuser:
        coupons = Coupon.objects.all()
        context = {
            'coupons': coupons
        }
        return render(request, 'adminpanel/coupon_management.html', context)


def add_coupon(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            code = request.POST.get('code')
            discount_type = request.POST.get('discount_typeSelect')
            discount_value = request.POST.get('discount_value')
            max_discount_amount = request.POST.get('max_discount_amount')
            activation_date = request.POST.get('activation_date')
            expiration_date = request.POST.get('expiration_date')
            is_onetime_usable = request.POST.get('onetimeusable')
            minimum_purchase_amount = request.POST.get('minimum_purchase_amount')

            # Parse the date-time values from the form input
            activation_date = timezone.datetime.strptime(activation_date, '%Y-%m-%dT%H:%M')
            expiration_date = timezone.datetime.strptime(expiration_date, '%Y-%m-%dT%H:%M')

            # Convert the 'is_onetime_usable' value to a boolean
            is_onetime_usable = True if is_onetime_usable == 'on' else False

            # Create and save the new coupon object
            coupon = Coupon(
                code=code,
                discount_type=discount_type,
                discount_value=discount_value,
                max_discount_amount=max_discount_amount,
                minimum_purchase_amount=minimum_purchase_amount,
                activation_date=activation_date,
                expiration_date=expiration_date,
                is_onetime_usable=is_onetime_usable
            )
            coupon.save()

            return redirect('coupon_management')
        return render(request, 'adminpanel/add_coupon.html')


def add_coupon(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            code = request.POST.get('code')
            discount_type = request.POST.get('discount_typeSelect')
            discount_value = request.POST.get('discount_value')
            min_or_max_amount = request.POST.get('min_or_max_amount')
            activation_date = request.POST.get('activation_date')
            expiration_date = request.POST.get('expiration_date')
            is_onetime_usable = request.POST.get('onetimeusable', False) == 'True'

            # Parse the date-time values from the form input
            activation_date = timezone.datetime.strptime(activation_date, '%Y-%m-%dT%H:%M')
            expiration_date = timezone.datetime.strptime(expiration_date, '%Y-%m-%dT%H:%M')

            # Create and save the new coupon object
            coupon = Coupon(
                code=code,
                discount_type=discount_type,
                discount_value=discount_value,
                min_or_max_amount=min_or_max_amount,
                activation_date=activation_date,
                expiration_date=expiration_date,
                is_onetime_usable=is_onetime_usable,
            )
            coupon.save()

            return redirect('coupon_management')
        return render(request, 'adminpanel/add_coupon.html')


def edit_coupon(request, coupon_id):
    if request.user.is_superuser:
        coupon = get_object_or_404(Coupon, pk=coupon_id)

        if request.method == 'POST':
            code = request.POST.get('code')
            discount_type = request.POST.get('discount_typeSelect')
            discount_value = request.POST.get('discount_value')
            min_or_max_amount = request.POST.get('min_or_max_amount')
            activation_date = request.POST.get('activation_date')
            expiration_date = request.POST.get('expiration_date')
            is_onetime_usable = request.POST.get('onetimeusable', False) == 'True'

            # Parse the date-time values from the form input
            activation_date = timezone.datetime.strptime(activation_date, '%Y-%m-%dT%H:%M')
            expiration_date = timezone.datetime.strptime(expiration_date, '%Y-%m-%dT%H:%M')

            # Update the coupon object with new values
            coupon.code = code
            coupon.discount_type = discount_type
            coupon.discount_value = discount_value
            coupon.min_or_max_amount = min_or_max_amount
            coupon.activation_date = activation_date
            coupon.expiration_date = expiration_date
            coupon.is_onetime_usable = is_onetime_usable

            # Save the updated coupon object
            coupon.save()

            return redirect('coupon_management')

        context = {
            'coupon': coupon,
        }
        return render(request, 'adminpanel/edit_coupon.html', context)


def activate_coupon(request, coupon_id, action):
    if request.user.is_superuser:
        coupon = Coupon.objects.get(id=coupon_id)
        if action == 'activate':
            coupon.is_active = True
        else:
            coupon.is_active = False
        coupon.save()
        return redirect('coupon_management')


def dashboard(request):
    if request.user.is_superuser:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if not start_date_str or not end_date_str:
            # Default to last 30 days if no date range provided
            first_order = Order.objects.all().first()
            start_date = first_order.order_date.date() if first_order else date.today()
            end_date = now()
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.min.time()) + timedelta(days=1)

        # Calculate the number of 3-day intervals between start_date and end_date
        num_intervals = (end_datetime - start_datetime).days // 3 + 1
        # Generate the date_range based on the calculated number of intervals
        date_range = [start_datetime + timedelta(days=3 * i) for i in range(num_intervals)]
        sales_data = []

        for date in date_range:
            # Calculate the end of the 3-day interval
            interval_end = date + timedelta(days=2)

            total_sales = Order.objects.filter(
                order_date__range=[date, interval_end],  # Use range filter for the interval
            ).aggregate(total_sales=Sum('price'))['total_sales'] or Decimal('0.00')

            sales_data.append(float(total_sales))  # Convert Decimal to float

        # Serialize data
        serialized_date_range = json.dumps([date.strftime('%Y-%m-%d') for date in date_range])
        serialized_sales_data = json.dumps(sales_data)

        today = date.today()
        today_sales = Order.objects.filter(
            order_date__date=today,
        ).aggregate(total_sales=Sum('price'))['total_sales'] or Decimal('0.00')

        total_sales = Order.objects.filter(payment_status='PAID').aggregate(total_sales=Sum('price'))['total_sales'] or Decimal('0.00')

        # Calculate today's orders
        today = date.today()
        today_orders = Order.objects.filter(order_date__date=today).count()

        # Calculate total orders
        total_orders = Order.objects.count()

        categories = Category.objects.all()
        data = []
        for category in categories:
            product_count = Book.objects.filter(category=category).count()
            data.append(product_count)

        recent_orders = Order.objects.all().order_by('-id')[:8]

        context = {
            'date_range': serialized_date_range,
            'sales_data': serialized_sales_data,
            'today_sales': float(today_sales),
            'total_sales': float(total_sales),
            'today_orders': today_orders,
            'total_orders': total_orders,
            'categories': categories,
            'data': data,
            'recent_orders': recent_orders,
        }

        return render(request, 'adminpanel/dashboard.html', context)


def sales_report(request):
    if request.user.is_superuser:
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        # Today's totals
        today_orders = Order.objects.filter(order_date__date=today)
        order_count_today = today_orders.count()
        total_price_today = today_orders.aggregate(Sum('price'))['price__sum']
        # Weekly totals
        week_orders = Order.objects.filter(order_date__range=[week_ago, today])
        order_count_week = week_orders.count()
        total_price_week = week_orders.aggregate(Sum('price'))['price__sum']
        # Monthly totals
        month_orders = Order.objects.filter(order_date__range=[month_ago, today])
        order_count_month = month_orders.count()
        total_price_month = month_orders.aggregate(Sum('price'))['price__sum']
        # Top selling products
        top_selling_products_today = OrderItem.objects.filter(order__order_date__range=[today, today]).values('variant__book__name').annotate(
            total_quantity=Sum('quantity')).order_by('-total_quantity')[:5] if not None else 0

        top_selling_products_week = OrderItem.objects.filter(
            order__order_date__range=[week_ago, today]
        ).values('variant__book__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
        top_selling_products_month = OrderItem.objects.filter(order__order_date__range=[month_ago, today]).values(
            'variant__book__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
        context = {
            'order_count_today': order_count_today,
            'total_price_today': total_price_today,
            'order_count_week': order_count_week,
            'total_price_week': total_price_week,
            'order_count_month': order_count_month,
            'total_price_month': total_price_month,
            'top_selling_products_today': top_selling_products_today,
            'top_selling_products_week': top_selling_products_week,
            'top_selling_products_month': top_selling_products_month,
        }
        return render(request, 'adminpanel/sales_report.html', context)

    # def sale(request):
    #     end_date = datetime.now()
    #     start_date = end_date - timedelta(days=30)
    #
    #     sales_data = Order.objects.filter(
    #         order_date__range=[start_date, end_date],
    #         payment_status='PAID'
    #     ).annotate(sales_date=models.functions.TruncDate('order_date')).values(
    #         'sales_date'
    #     ).annotate(total_sales=Count('id')).order_by('sales_date')
    #
    #     labels = [entry['sales_date'].strftime('%Y-%m-%d') for entry in sales_data]
    #     data = [entry['total_sales'] for entry in sales_data]
    #
    #     return render(request, 'sales_chart.html', {'labels': labels, 'data': data})
    #
    # def get_sales_data(request):
    #     start_date = request.GET.get('start_date')
    #     end_date = request.GET.get('end_date')
    #
    #     if not start_date or not end_date:
    #         # Default to last 30 days if no date range provided
    #         end_date = now()
    #         start_date = end_date - timedelta(days=30)
    #
    #     sales_data = Order.objects.filter(
    #         order_date__gte=start_date,
    #         order_date__lte=end_date,
    #         payment_status='PAID'
    #     ).annotate(
    #         sales_date=models.Cast('order_date', models.DateField())
    #     ).values('sales_date').annotate(total_sales=Count('id')).order_by('sales_date')
    #
    #     data = {
    #         'labels': [entry['sales_date'].strftime('%Y-%m-%d') for entry in sales_data],
    #         'data': [entry['total_sales'] for entry in sales_data]
    #     }
    #
    #     return JsonResponse(data)
