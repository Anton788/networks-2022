from django.contrib import admin
from .models import Product, ProductImage, Tag, ProductFile, \
                    ProductsProcessingFile, ProductRating, ProductTable
# Register your models here.


class TagProductInline(admin.TabularInline):
    model = Product.tags.through


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'factory',)
    search_fields = ('name', 'tags_text')
    readonly_fields = ('id',)
    exclude = ('tags', )
    inlines = [
        TagProductInline
    ]

    def get_fieldsets(self, request, obj=None):

        return (
            ('Information', {'fields': ('name', 'id', 'price', 'factory', 'company', 
                                        'description', 'condition', 'meta_information', 
                                        'factory_producer', 'company_producer', 'is_available')}),
            ('Search', {'fields': ('tags_text',)}),
            ('Media', {'fields': ('main_image',)}),
        )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'photo',)
    search_fields = ('product', 'photo',)


@admin.register(ProductFile)
class ProductFileAdmin(admin.ModelAdmin):
    list_display = ('product', 'document',)
    search_fields = ('product', 'document',)


@admin.register(ProductsProcessingFile)
class ProductsProcessingFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'datetime')
    search_fields = ('name', 'link',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', 'description')
    
    

@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'company', 'rating', 'description', 'last_changed_at')
    search_fields = ('product', 'company', 'rating', 'description', 'last_changed_at')
    
    
@admin.register(ProductTable)
class ProductTableAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'link',)
    search_fields = ('name', 'created_at', 'link',)

