from django.contrib import admin
from .models import LaundryOrder, OrderTracking


class OrderTrackingInline(admin.StackedInline):
    model = OrderTracking
    extra = 0


@admin.register(LaundryOrder)
class LaundryOrderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'full_name', 'mobile', 'city', 'laundry_type', 'issued_date', 'delivery_date', 'created_at']
    list_filter = ['state', 'laundry_type', 'issued_date']
    search_fields = ['full_name', 'mobile', 'city']
    inlines = [OrderTrackingInline]


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'updated_at']
    list_filter = ['status']
