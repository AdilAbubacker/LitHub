from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from image_cropping.fields import ImageCropField


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to='category_images/')
    offer_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(null=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate slug from the name field
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Author(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    image = models.ImageField(default='default_author.jpg', upload_to='author_images/')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Publisher(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CoverType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Language(models.Model):
    name = models.CharField(default='English', max_length=50)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Book(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    no_of_pages = models.PositiveSmallIntegerField()
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    offer_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    description = models.TextField()
    cover_image = ImageCropField(upload_to='book_covers/')
    is_active = models.BooleanField(default='True')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BookVariant(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    cover_type = models.ForeignKey(CoverType, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    offer_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    offer_percentage = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='variant_cover_image/')
    is_active = models.BooleanField(default='True')
    stock = models.PositiveIntegerField()
    slug = models.SlugField(max_length=255)

    def calculate_offer_price(self):
        category_offer = self.book.category.offer_percentage if self.book.category.offer_percentage else 0
        product_offer = self.book.offer_percentage if self.book.offer_percentage else 0
        variant_offer = max(category_offer, product_offer)
        self.offer_price = self.price * (1 - variant_offer / 100) if variant_offer != 0 else None
        self.offer_percentage = variant_offer if variant_offer != 0 else 0

    def save(self, *args, **kwargs):
        self.calculate_offer_price()
        self.slug = slugify(f"{self.book.name}-{self.cover_type.name}-{self.language.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.name}-{self.cover_type.name}-{self.language.name}"


@receiver(post_save, sender=Category)
@receiver(post_save, sender=Book)
def update_offer_prices_for_variants(sender, instance, **kwargs):
    variants = BookVariant.objects.filter(book__category=instance) if isinstance(instance, Category) else BookVariant.objects.filter(book=instance)
    for variant in variants:
        variant.calculate_offer_price()
        variant.save()


class VariantImages(models.Model):
    image = models.ImageField(upload_to='variant_images/')
    book_variant = models.ForeignKey(BookVariant, on_delete=models.CASCADE)

    def __str__(self):
        return f"Variant: {self.book_variant} - Image: {self.image.name}"
