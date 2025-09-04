from django.contrib import admin
from .models import Order, Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "user", "product", "total_amount", "status", "created_at")
    list_filter = ("status", "created_at", "product")
    search_fields = ("order_id", "user__username", "user__email", "product__name")