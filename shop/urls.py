from django.urls import path
from shop.views import *
from . import views
app_name = "shop"

urlpatterns = [
    path('', HomeView.as_view(), name="homepage"),
    path('product/', ProductView.as_view(), name="product"),
    path('search', SearchListView.as_view(), name='search'),
    path('product_detail/<slug>', ProductDetailView.as_view(), name="product_detail"),
    path('editreview/<int:review_id>', views.edit_review, name="edit_review"),
    path('delreview/<int:review_id>', views.del_review, name="del_review"),
    path('addreview/<int:id>/', views.add_review, name="addreview"),
    path('cat/<id>', views.cat, name="cat"),
    path('brand/<id>', views.brand, name="brand"),
    path('type/<id>', views.type, name="type"),
    path('add-to-cart/<slug>', AddToCart.as_view(), name="add-to-cart"),
    path('wishlist/<slug>', WishlistView.as_view(), name="wishlist"),
    path('add-coupon/', AddCouponView.as_view(), name="add-coupon"),
    path('checkout/', CheckOutView.as_view(), name="checkout"),
    path('remove-from-cart/<slug>', RemoveCartView.as_view(), name="remove-from-cart"),
    path('remove-item/<slug>', RemoveItem.as_view(), name="remove-item"),
    path('remove-wishlistitem/<slug>', RemoveWishlistItem.as_view(), name="remove-wishlistitem"),
    path('order_summary', OrderSummaryView.as_view(), name="order_summary"),
    path('wishlist_summary', WishlistSummary.as_view(), name="wishlist_summary"),
    path('payment/', PaymentView.as_view(), name="payment"),
    path('myorder/', MyOrderView.as_view(), name="myorder"),

]