from django.db import models
from shop.models import Product
from decimal import Decimal
from django.core.validators import MinValueValidator,MaxValueValidator
from coupons.models import Coupon
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class Order(models.Model):

    first_name = models.CharField(_('first name'),
                                  max_length=50)
    last_name = models.CharField(_('last name'),
                                 max_length=50)
    email = models.EmailField(_('e-mail'))
    phone_regex = RegexValidator(regex=r'^\+?0?\d{9,15}$', message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))
    phone_number = models.CharField(_('phone_number'),validators=[phone_regex], max_length=15, blank=False,default=999999999) # validators should be a list
    address = models.CharField(_('address'),max_length=250)
    postal_code = models.CharField(_('postal code'),max_length=20)
    city = models.CharField(_('city'),max_length=100)
    country = models.CharField(_('city'), max_length=100,default = "iran")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    braintree_id = models.CharField(max_length=150, blank=True)
    coupon = models.ForeignKey(Coupon,
                               related_name='orders',
                               null=True,
                               blank=True,
                               on_delete=models.SET_NULL)
    discount = models.IntegerField(default=0,
                                   validators=[MinValueValidator(0),
                                               MaxValueValidator(100)])

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        total_cost = sum(item.get_cost() for item in self.items.all())
        return total_cost - total_cost * \
               (self.discount / Decimal('100'))

class OrderItem(models.Model):

    order = models.ForeignKey(Order,
        related_name='items',
        on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
        related_name='order_items',
        on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity