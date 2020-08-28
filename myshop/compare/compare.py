from decimal import Decimal
from django.conf import settings
from shop.models import Product
from coupons.models import Coupon

class Compare(object):

    def __init__(self, request):

        self.session = request.session
        compare = self.session.get(settings.COMPARE_SESSION_ID)
        # store current applied coupon
        self.coupon_id = self.session.get('coupon_id')

        if not compare:
            # save an empty cart in the session
            compare = self.session[settings.COMPARE_SESSION_ID] = {}
        self.compare = compare

    def add(self, product, quantity=1, update_quantity=False):

        product_id = str(product.id)
        if product_id not in self.compare:
            self.compare[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.compare[product_id]['quantity'] = quantity
        else:
            self.compare[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):

        product_id = str(product.id)
        if product_id in self.compare:
            del self.compare[product_id]
        self.save()

    def __iter__(self):

        product_ids = self.compare.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        compare = self.compare.copy()
        for product in products:
            compare[str(product.id)]['product'] = product
        for item in compare.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.compare.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in
                   self.compare.values())

    def clear(self):
        del self.session[settings.COMPARE_SESSION_ID]
        self.save()

    @property
    def coupon(self):
        if self.coupon_id:
            return Coupon.objects.get(id=self.coupon_id)

        return None

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal('100')) \
                   * self.get_total_price()

        return Decimal('0')

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()