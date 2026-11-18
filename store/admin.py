from django.contrib import admin
from .models import Wholesaler, Category, Product, ProductImage, Variant, HeroBanner, Order, OrderItem



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 2

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'wholesaler', 'base_price', 'is_active')
    list_filter = ('wholesaler', 'categories', 'is_active')
    search_fields = ('name', 'wholesaler__name')
    # This gives you a dual-box selector for picking multiple categories
    filter_horizontal = ('categories',) 
    inlines = [ProductImageInline, VariantInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug')
    prepopulated_fields = {'slug': ('name',)} # Auto-fills slug in admin UI as you type
    search_fields = ('name',)

@admin.register(Wholesaler)
class WholesalerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'location')

admin.site.register(ProductImage)
admin.site.register(Variant)

@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ('position', 'title', 'is_active')
    list_editable = ('is_active',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product', 'variant', 'wholesaler']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'phone', 'city', 'paid', 'status', 'created']
    list_filter = ['paid', 'status', 'created']
    search_fields = ['first_name', 'last_name', 'phone']
    inlines = [OrderItemInline]