from django.shortcuts import redirect, get_object_or_404,render, HttpResponse
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import DeleteView, UpdateView
from shop.models import *
from shop.forms import *
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
import random
import string
from django.db.models import Q


class HomeView(ListView):
    model = Products
    template_name = 'home.html'
    paginate_by = 9

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['brand'] = BrandName.objects.all()
        context['type'] = Type.objects.all()
        context['category'] = Category.objects.all()
        context['cat'] = CategoriesName.objects.all()
        return context



def create_txn_id():
    return '' .join(random.choices(string.ascii_lowercase + string.digits, k=20))


class ProductView(ListView):
    model = Products
    template_name = 'product.html'
    paginate_by = 9

    def get_context_data(self,*args, **kwargs):
        context = super(ProductView, self).get_context_data(**kwargs)
        context['brand'] = BrandName.objects.all()
        context['type'] = Type.objects.all()
        context['product'] = Products.objects.all()
        context['category'] = CategoriesName.objects.all()
        return context


class ProductDetailView(DetailView):
    model = Products
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['category'] = CategoriesName.objects.all()
        context['review'] = Review.objects.filter(product=self.object)
        context['type'] = Type.objects.all()
        context['releated_products'] = Products.objects.exclude(slug=self.kwargs["slug"])
        return context


class AddToCart(LoginRequiredMixin, View):
    def get(self,request,slug, *args, **kwargs):
        product = get_object_or_404(Products, slug=slug)

        order_product, create = OrderItem.objects.get_or_create(
            item=product,
            user=request.user,
            ordered=False
        )
        order_query = Order.objects.filter(user=request.user, ordered=False)
        if order_query.exists():
            order = order_query[0]
            if order.items.filter(item__slug=slug).exists():
                order_product.qty += 1
                order_product.save()
                messages.success(self.request, "item updated Succesfuly")
            else:
                order.items.add(order_product)

            return redirect("shop:order_summary")
        else:
            add_date = timezone.now()
            order = Order.objects.create(user=request.user, add_date=add_date, ordered=False)
            order.items.add(order_product)
            return redirect("shop:order_summary")


class RemoveCartView(LoginRequiredMixin, View):
    def get(self, request, slug, *args, **kwargs):
        item = get_object_or_404(Products, slug=slug)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False,
        )
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False
                )[0]
                if order_item.qty > 1:
                    order_item.qty -= 1
                    order_item.save()
                    # todo :your cart is updated
                    messages.success(self.request, "item updated Succesfuly")
                else:
                    order.items.remove(order_item)
                    messages.success(self.request, "item updated Succesfuly")
                return redirect("shop:order_summary")
            else:
                return redirect("shop:order_summary")
        else:
            return redirect("shop:order_summary")


class RemoveItem(LoginRequiredMixin, View):
    def get(self, request, slug, *args, **kwargs):
        item = get_object_or_404(Products, slug=slug)
        order_qs = Order.objects.filter(
            ordered=False,
            user=request.user
        )
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
                order.items.remove(order_item)
                order_item.delete()
                messages.warning(self.request, "Your cart is empty")
                return redirect("shop:order_summary")
            else:
                return redirect("shop:order_summary")
        else:
            return redirect("shop:order_summary")


class OrderSummaryView(ListView):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            type = Type.objects.all()
            form = CouponForm()
            context = {"order": order, "form": form, "type":type}
        except ObjectDoesNotExist:
            return redirect("shop:homepage")
        return render(self.request, "order_summary.html", context)


def check_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return True
    except ObjectDoesNotExist:
        return False


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.warning(request, "this coupon does not exists")
        return redirect("shop:order_summary")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        if self.request.method == "POST":
            form = CouponForm(self.request.POST or None)

            if form.is_valid():
                code = form.cleaned_data.get('code')
                if check_coupon(self.request, code):
                    order = Order.objects.get(user=self.request.user, ordered=False)
                    order.coupon = get_coupon(self.request, code)
                    order.save()
                    messages.success(self.request, "msg coupon add successfully")
                    return redirect("shop:order_summary")
                else:
                    messages.error(self.request, "invalid Coupon")
                    return redirect("shop:order_summary")
            else:
                return redirect("shop:order_summary")


class CheckOutView(LoginRequiredMixin, View):
    def get(self,request,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckOutForm()

            context = {
                "order": order,
                "form": form,
                "type":Type.objects.all(),
                'address': Address.objects.filter(user=self.request.user)
            }
            return render(self.request, "checkout.html", context)

        except ObjectDoesNotExist:
            messages.error(self.request, "you have not active order")
            return redirect("shop:order_summary")

    def post(self, *args, **kwargs):
        form = CheckOutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if self.request.method == "POST":
                save_address = self.request.POST.get("save_address", None)

                if save_address is not None:
                    selected_address = Address.objects.get(id=save_address)
                    order.address = selected_address
                    order.save()
                    return redirect("shop:payment")

                else:
                    if form.is_valid():
                        data = form.save(commit=False)
                        data.user = self.request.user
                        data.default = True
                        data.save()

                        order.address = data
                        order.save()
                        return redirect("shop:payment")

                    else:
                        messages.warning(self.request, "please check data")
                        return redirect("shop:checkout")

        except ObjectDoesNotExist:
            messages.error(self.request, "not found any active order")
            return redirect("shop:order_summary")


class PaymentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if not order.address:
            return redirect("shop:checkout")
        else:
            context = {
                "order": order,
                'type': Type.objects.all()
            }
            return render(self.request, "payment.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if self.request.POST.get("payment") == "cod":
            pay = Payment()
            pay.user = self.request.user
            pay.ammount = order.grand_total()
            pay.txn_id = create_txn_id()
            pay.order_id = order
            pay.save()
            order_item = Order.objects.all()
            order_item.update(ordered=True)
            for item in order_item:
                item.save()

                order.ordered = True
                order.ordered_date = timezone.now()
                order.save()
                return redirect("shop:homepage")


class MyOrderView(View):
    def get(self, request, *args, **kwargs):
        context = {
            "order": Order.objects.filter(user=self.request.user, ordered=True),
            'type':Type.objects.all()
        }
        return render(self.request, "MyOrder.html", context)


class SearchListView(ListView):
    model = Products
    template_name = "search.html"

    def get_queryset(self):
        product = Products.objects.all()
        query = self.request.GET.get("search", None)

        if query:
            cond = Q(name__icontains=query) | Q(category__cat_title__icontains=query) | Q(brand__brand_name=query) | Q(type__title=query)
            return product.filter(cond)
        return product

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SearchListView, self).get_context_data(**kwargs)
        context['brand'] = BrandName.objects.all()
        context['type'] = Type.objects.all()
        context['category'] = CategoriesName.objects.all()
        return context


def cat(r, id):
    return render(r, 'cat.html', {
        'type':Type.objects.all(),
        'category':CategoriesName.objects.all(),
        'brand': BrandName.objects.all(),
        'product': Products.objects.filter(category_id=id)
    })


def type(r, id):
    return render(r, 'cat.html', {
        'type':Type.objects.all(),
        'category':CategoriesName.objects.all(),
        'brand': BrandName.objects.all(),
        'product': Products.objects.filter(type_id=id)
    })


def brand(r, id):
    return render(r, 'cat.html', {
        'type': Type.objects.all(),
        'category': CategoriesName.objects.all(),
        'brand': BrandName.objects.all(),
        'product': Products.objects.filter(brand_id=id)
    })


def add_review(r, id):
    product = Products.objects.get(id=id)
    if r.method == "POST":
        form = AddReviewForm(r.POST or None)
        if form.is_valid():
            data = form.save(commit=False)
            data.product = product
            data.user = r.user
            data.save()
            return redirect('shop:product_detail', product.slug)
    else:
        form = AddReviewForm()
    return render(r, 'product_detail.html', {
        'form': form,
    })


def edit_review(r, review_id):
    review = Review.objects.get(id=review_id)
    if r.method == "POST":
        form = AddReviewForm(r.POST, instance=review)
        if form.is_valid():
            data = form.save(commit=False)
            if (data.rating > 10) or (data.rating < 0):
                error = "Out of range from 0 to 10"
                return render(r, 'edit_review.html', {
                    'error': error,
                    'form': form
                })
            else:
                data.save()
                return redirect('shop:product_detail', review.product.slug)
    else:
        form = AddReviewForm(instance=review)
        return render(r, 'edit_review.html', {
            'form': form,

        })


def del_review(r, review_id):
    review = Review.objects.get(id=review_id)
    if review.user.email:
        review.delete()
        return redirect('shop:product_detail', review.product.slug)


class WishlistView(View):
    def get(self,request,slug, *args, **kwargs):
        product = get_object_or_404(Products, slug=slug)

        order_product, create = OrderItem.objects.get_or_create(
            item=product,
            user=request.user,
            ordered=False
        )
        order_query = Order.objects.filter(user=request.user, ordered=False)
        if order_query.exists():
            order = order_query[0]
            if order.items.filter(item__slug=slug).exists():
                order_product.qty += 1
                order_product.save()
                messages.success(self.request, "item updated Succesfuly")
            else:
                order.items.add(order_product)

            return redirect("shop:wishlist_summary")
        else:
            add_date = timezone.now()
            order = Order.objects.create(user=request.user, add_date=add_date, ordered=False)
            order.items.add(order_product)
            return redirect("shop:wishlist_summary")


class WishlistSummary(ListView):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            type = Type.objects.all()
            category = Category.objects.all()
            cat = CategoriesName.objects.all()
            context = {"order": order, "type": type, "category":category, "cat":cat}
        except ObjectDoesNotExist:
            return redirect("shop:homepage")
        return render(self.request, "wishlist.html", context)


class RemoveWishlistItem(LoginRequiredMixin, View):
    def get(self, request, slug, *args, **kwargs):
        item = get_object_or_404(Products, slug=slug)
        order_qs = Order.objects.filter(
            ordered=False,
            user=request.user
        )
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
                order.items.remove(order_item)
                order_item.delete()
                messages.warning(self.request, "Your cart is empty")
                return redirect("shop:wishlist_summary")
            else:
                return redirect("shop:wishlist_summary")
        else:
            return redirect("shop:wishlist_summary")

