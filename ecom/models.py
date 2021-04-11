from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.utils.text import slugify


class Categories(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("ecom:categories", kwargs={
            'slug': self.slug                                       #
    })

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Categories, self).save(*args, **kwargs)


class Brand(models.Model):
    brand_name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("ecom:brand", kwargs={
            'slug': self.slug
    })

    def __str__(self):
        return self.brand_name

    def save(self,*args, **kwargs):
        self.slug = slugify(self.brand_name)
        super(Brand, self).save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(null=True, blank=True)
    price = models.FloatField()
    image = models.ImageField(blank=True, null=True)
    discount_price = models.FloatField(null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("ecom:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart(self):
        return reverse("ecom:add-to-cart", kwargs={
            'slug': self.slug
        })
    def get_remove_from_cart_url(self):
        return reverse("ecom:remove-from-cart", kwargs={
            "slug": self.slug
        })

    def save(self,*args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args,**kwargs)


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)

    def __str__(self):
        return self.item.name

    def total_actual_ammount(self):
        return self.qty * self.item.price

    def total_discount_ammount(self):
        return self.qty * self.item.discount_price

    def saving_ammount(self):
        return self.total_actual_ammount() - self.total_discount_ammount()

    def payable_ammount(self):
        if self.item.discount_price:
            return self.total_discount_ammount()
        else:
            return self.total_actual_ammount()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField(null=True)
    add_date = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, blank=True, null=True)

    def grand_total(self):
        total = 0
        for oi in self.items.all():
            total += oi.payable_ammount()

            if self.coupon:
                total -= (total * self.coupon.percentage) / 100
        return total

    def get_coupon_ammount(self):
        total = 0
        for oi in self.items.all():
            total += oi.payable_ammount()
        return (total * self.coupon.percentage) / 100


class Coupon(models.Model):
    code = models.CharField(max_length=200)
    percentage = models.IntegerField()

    def __str__(self):
        return self.code


TYPE_CHOICE = {
    ("W","WORK"),
    ("H","HOME"),
}


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    contact = models.IntegerField()
    pin = models.IntegerField()
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    landmark = models.CharField(max_length=200)
    alternative_no = models.IntegerField()
    default = models.BooleanField(default=False)
    address_type = models.CharField(choices=TYPE_CHOICE, max_length=2)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Addressess"


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    txn_id = models.CharField(max_length=200)
    ammount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    order_id = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username
