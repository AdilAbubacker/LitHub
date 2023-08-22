from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Book)
admin.site.register(Category)
admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(CoverType)
admin.site.register(Language)
admin.site.register(BookVariant)
admin.site.register(VariantImages)


