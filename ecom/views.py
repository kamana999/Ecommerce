from django.shortcuts import redirect, get_object_or_404,render
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import DeleteView, UpdateView
from ecom.models import *
from ecom.forms import *
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
import random
import string


class HomeView(ListView):
    model = Product
    paginate_by = 10
    template_name = 'home.html'


def create_txn_id():
    return '' .join(random.choices(string.ascii_lowercase + string.digits, k=20))


class ProductView(DetailView):
    model = Product
    template_name = 'product.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, *args, **kwargs):
        context = super(ProductView, self).get_context_data(*args, **kwargs)
        context['releated_products'] = Product.objects.exclude(slug=self.kwargs["slug"])
        return context


class RemoveCartView(LoginRequiredMixin, View):
    def get(self, request, slug, *args, **kwargs):
        item = get_object_or_404(Product, slug=slug)
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
                return redirect("ecom:order_summary")
            else:
                return redirect("ecom:order_summary")
        else:
            return redirect("ecom:order_summary")


class RemoveItem(LoginRequiredMixin, View):
    def get(self, request, slug, *args, **kwargs):
        item = get_object_or_404(Product, slug=slug)
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
                return redirect("ecom:order_summary")
            else:
                return redirect("ecom:order_summary")
        else:
            return redirect("ecom:order_summary")


class AddToCart(LoginRequiredMixin, View):
    def get(self, request,slug,*args,**kwargs):
        product = get_object_or_404(Product, slug=slug)

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

            return redirect("ecom:order_summary")
        else:
            add_date = timezone.now()
            order = Order.objects.create(user=request.user, add_date=add_date,ordered=False)
            order.items.add(order_product)
            return redirect("ecom:order_summary")


class OrderSummaryView(ListView):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=request.user, ordered=False)
            form = CouponForm()
            context = {"order": order, "form": form}
        except ObjectDoesNotExist:
            return redirect("ecom:homepage")
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
        return redirect("ecom:order_summary")


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
                    return redirect("ecom:order_summary")
                else:
                    messages.error(self.request, "invalid Coupon")
                    return redirect("ecom:order_summary")
            else:
                return redirect("ecom:order_summary")


class CheckOutView(LoginRequiredMixin, View):
    def get(self,request,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckOutForm()

            context = {
                "order": order,
                "form": form,
                'address': Address.objects.filter(user=self.request.user)
            }
            return render(self.request, "checkout.html", context)

        except ObjectDoesNotExist:
            messages.error(self.request, "you have not active order")
            return redirect("ecom:order_summary")

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
                    return redirect("ecom:payment")

                else:
                    if form.is_valid():
                        data = form.save(commit=False)
                        data.user = self.request.user
                        data.default = True
                        data.save()

                        order.address = data
                        order.save()
                        return redirect("ecom:checkout")

                    else:
                        messages.warning(self.request, "please check data")
                        return redirect("ecom:checkout")

        except ObjectDoesNotExist:
            messages.error(self.request, "not found any active order")
            return redirect("ecom:order_summary")


class PaymentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if not order.address:
            return redirect("ecom:checkout")
        else:
            context = {
                "order": order
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
                return redirect("ecom:homepage")


class MyOrderView(View):
    def get(self, request, *args, **kwargs):
        context = {
            "order": Order.objects.filter(user=self.request.user, ordered=True)
        }
        return render(self.request, "MyOrder.html", context)








