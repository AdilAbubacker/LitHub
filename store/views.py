from django.core.paginator import Paginator
from django.db.models import Sum, Count, Subquery, OuterRef
from django.shortcuts import render
from cart.models import Cart, CartItem, WishlistItem
from store.models import Book, Category, VariantImages, BookVariant, Language, CoverType


# Create your views here.
def home(request):
    categories = Category.objects.all()
    books = Book.objects.all()
    cart_count = CartItem.objects.filter(
        cart__user=request.user.id).aggregate(Sum('quantity'))['quantity__sum']
    wishlist_count = WishlistItem.objects.filter(
        wishlist__user=request.user.id).aggregate(Count('variant'))['variant__count']
    context = {
        'categories': categories,
        'books': books,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count
    }
    return render(request, 'store/home.html', context)


def about(request):
    return render(request, 'store/about.html')


def contact(request):
    return render(request, 'store/contact.html')


def product_list(request, category, slug):
    search = request.GET.get('q')
    sort = request.GET.get('sort')
    heading = slug

    if category == 'Category':
        if slug == 'all':
            books = Book.objects.all()
            heading = 'All Books'
        else:
            books = Book.objects.filter(category__slug=slug)
            heading = Category.objects.get(slug=slug).name
        is_variant = False
    elif category == 'Language':
        language = Language.objects.get(slug=slug)
        books = BookVariant.objects.filter(language=language).distinct('book')
        book_ids = [book.id for book in books]
        books = BookVariant.objects.filter(id__in=book_ids)
        heading = language.name
        is_variant = True
    elif category == 'CoverType':
        cover_type = CoverType.objects.get(slug=slug)
        books = BookVariant.objects.filter(cover_type=cover_type)
        heading = cover_type.name
        is_variant = True

    if search:
        if is_variant:
            books = books.filter(book__name__icontains=search)
        else:
            books = books.filter(name__icontains=search)

    if sort:
        if sort == 'atoz':
            books = books.order_by('book__name') if is_variant else books.order_by('name')
            sort = 'A to Z'
        elif sort == 'discount':
            if is_variant:
                books = books.order_by('-offer_percentage', '-price')
            else:
                subquery = BookVariant.objects.filter(book_id=OuterRef('id')).order_by('id')
                books = books.annotate(first_variant_offer_percentage=Subquery(subquery.values('offer_percentage')[:1]))
                books = books.annotate(first_variant_price=Subquery(subquery.values('price')[:1]))
                books = books.order_by('-first_variant_offer_percentage', '-first_variant_price')
            sort = 'Discount'
        elif sort == 'pricelth':
            if is_variant:
                books = books.order_by('price')
            else:
                subquery = BookVariant.objects.filter(book_id=OuterRef('id')).order_by('id')
                books = books.annotate(first_variant_price=Subquery(subquery.values('price')[:1]))
                books = books.order_by('first_variant_price')
            sort = 'Price: Low to High'
        elif sort == 'pricehtl':
            if is_variant:
                books = books.order_by('-price')
            else:
                subquery = BookVariant.objects.filter(book_id=OuterRef('id')).order_by('id')
                books = books.annotate(first_variant_price=Subquery(subquery.values('price')[:1]))
                books = books.order_by('-first_variant_price')
            sort = 'Price: High to Low'
        elif sort == 'newest':
            books = books.order_by('id')
            sort = 'Newest'
        elif sort == 'oldest':
            books = books.order_by('-id')
            sort = 'Oldest'
        else:
            sort = 'Sort by ↑↓'
    else:
        sort = 'Sort by ↑↓'

    paginator = Paginator(books, 6)
    page = request.GET.get('page')
    books = paginator.get_page(page)

    categories = Category.objects.all()
    cart_count = CartItem.objects.filter(
        cart__user=request.user.id).aggregate(Sum('quantity'))['quantity__sum']
    wishlist_count = WishlistItem.objects.filter(
        wishlist__user=request.user.id).aggregate(Count('variant'))['variant__count']
    languages = Language.objects.all()
    formats = CoverType.objects.all()

    context = {
        'books': books,
        'categories': categories,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'languages': languages,
        'formats': formats,
        'is_variant': is_variant,
        'sort': sort,
        'heading': heading,
    }
    return render(request, 'store/product_list.html', context)


def product_details(request, variant_slug):
    try:
        variant = BookVariant.objects.get(slug=variant_slug)
    except:
        variant = BookVariant.objects.filter(book__slug=variant_slug).first()

    book = variant.book
    language = variant.language
    cover_type_variants = book.bookvariant_set.filter(language=language)
    language_variants = book.bookvariant_set.select_related('language').distinct('language')
    images = variant.variantimages_set.all()
    cart_count = CartItem.objects.filter(
        cart__user=request.user.id).aggregate(Sum('quantity'))['quantity__sum']
    wishlist_count = WishlistItem.objects.filter(
        wishlist__user=request.user.id).aggregate(Count('variant'))['variant__count']
    wishlisted = WishlistItem.objects.filter(
        wishlist__user=request.user.id, variant=variant).exists()

    context = {
        'book': book,
        'variant': variant,
        'images': images,
        'cover_type_variants': cover_type_variants,
        'language_variants': language_variants,
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'wishlisted': wishlisted,
    }
    return render(request, 'store/product_details.html', context)


def user_profile(request):
    return render(request, 'store/user_profile.html')