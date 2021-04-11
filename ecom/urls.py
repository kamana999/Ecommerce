from django.urls import path
from ecom.views import *
app_name = "ecom"

urlpatterns = [
    path('', HomeView.as_view(), name="homepage"),
    path('product/<slug>', ProductView.as_view(), name="product"),
    path('add-to-cart/<slug>', AddToCart.as_view(), name="add-to-cart"),
    path('add-coupon/', AddCouponView.as_view(), name="add-coupon"),
    path('checkout/', CheckOutView.as_view(), name="checkout"),
    path('remove-from-cart/<slug>', RemoveCartView.as_view(), name="remove-from-cart"),
    path('remove-item/<slug>', RemoveItem.as_view(), name="remove-item"),
    path('order_summary', OrderSummaryView.as_view(), name="order_summary"),
    path('payment/', PaymentView.as_view(), name="payment"),
    path('myorder/', MyOrderView.as_view(), name="myorder"),
]