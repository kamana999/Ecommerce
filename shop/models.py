from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.utils.text import slugify


class Type(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    type_icon = models.ImageField(default=None, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Type, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("shop:type", kwargs={
            'slug': self.slug
        })


class CategoriesName(models.Model):
    cat_title = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(blank=True, null=True)
    type = models.ManyToManyField(Type, null=True, blank=True, default=None)
    cat_image = models.ImageField(default=None, blank=True, null=True)

    def __str__(self):
        return self.cat_title

    def get_absolute_url(self):
        return reverse("shop:categories", kwargs={
            'slug': self.slug  #
        })


class Category(models.Model):
    ca_id = models.AutoField(primary_key=True)
    categoryId = models.ForeignKey(CategoriesName, on_delete=models.CASCADE)
    typeId = models.ForeignKey(Type, on_delete=models.CASCADE)

    def __str__(self):
        return self.categoryId.cat_title


class BrandName(models.Model):
    brand_name = models.CharField(max_length=200)
    brand_logo = models.ImageField(upload_to='brand_logo')
    slug = models.SlugField(blank=True, null=True)

    def __str__(self):
        return self.brand_name

    def get_absolute_url(self):
        return reverse("shop:brand", kwargs={
            'slug': self.slug  #
        })


class Brands(models.Model):
    b_id = models.AutoField(primary_key=True)
    brand = models.ForeignKey(BrandName, on_delete=models.CASCADE)
    category = models.ForeignKey(CategoriesName, on_delete=models.CASCADE)


class Products(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(CategoriesName, on_delete=models.CASCADE)
    brand = models.ForeignKey(BrandName, on_delete=models.SET_NULL, null=True)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(null=True, blank=True)
    price = models.FloatField()
    image = models.ImageField(blank=True, null=True)
    image_high = models.ImageField(blank=True, null=True)
    discount_price = models.FloatField(null=True, blank=True)
    description = models.TextField()
    color = models.CharField(null=True, blank=True, max_length=200)
    weight = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:product_detail", kwargs={
            'slug': self.slug
        })

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Products, self).save(*args, **kwargs)

    def get_add_to_cart(self):
        return reverse("shop:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_wishlist(self):
        return reverse("shop:wishlist", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("shop:remove-from-cart", kwargs={
            "slug": self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Products, on_delete=models.CASCADE)
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
    ("W", "WORK"),
    ("H", "HOME"),
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


class Review(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField(max_length=1000)
    rating = models.FloatField(default=0)

    def __str__(self):
        return self.user.username


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    wished_item = models.ForeignKey(Products, on_delete=models.CASCADE)
    slug = models.CharField(max_length=30, null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wished_item.name

