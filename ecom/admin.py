from django.contrib import admin
from ecom.models import *

admin.site.register(Categories)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered_date', 'coupon', 'address', 'ordered']


class ProductAdmin(admin.ModelAdmin):
    pass


class BrandAdmin(admin.ModelAdmin):
    pass


class OrderItemAdmin(admin.ModelAdmin):
    pass


class CouponAdmin(admin.ModelAdmin):
    pass


class AdreesAdmin(admin.ModelAdmin):
    pass


class PaymentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, PaymentAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Address, AdreesAdmin)
admin.site.register(Payment, PaymentAdmin)
