from decimal import Decimal
from django.conf import settings
from shop.models import Product

class Compare(object):

    def __init__(self, request):

        self.session = request.session
        compare = self.session.get(settings.COMPARE_SESSION_ID)

        if not compare:
            # save an empty cart in the session
            compare = self.session[settings.COMPARE_SESSION_ID] = {}
        self.compare = compare

    def add(self, product):

        product_id = str(product.id)
        if product_id not in self.compare:
            self.compare[product_id] = {'price': str(product.price)}
        self.save()

    def save(self):
        self.session.modified = True


    def __iter__(self):

        product_ids = self.compare.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        compare = self.compare.copy()
        for product in products:
            compare[str(product.id)]['product'] = product
        for item in compare.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price']
            yield item

    def remove(self, product):

        product_id = str(product.id)
        if product_id in self.compare:
            del self.compare[product_id]
        self.save()
    #
    # def __iter__(self):
    #
    #     product_ids = self.compare.keys()
    #     # get the product objects and add them to the cart
    #     products = Product.objects.filter(id__in=product_ids)
    #     cart = self.cart.copy()
    #     for product in products:
    #         cart[str(product.id)]['product'] = product
    #     for item in cart.values():
    #         item['price'] = Decimal(item['price'])
    #         item['total_price'] = item['price'] * item['quantity']
    #         yield item

    # def __len__(self):
    #     return sum(item['quantity'] for item in self.cart.values())

    # def get_total_price(self):
    #     return sum(Decimal(item['price']) * item['quantity'] for item in
    #                self.cart.values())

    def clear(self):
        del self.session[settings.COMPARE_SESSION_ID]
        self.save()

    # @property
    # def coupon(self):
    #     if self.coupon_id:
    #         return Coupon.objects.get(id=self.coupon_id)
    #
    #     return None

    # def get_discount(self):
    #     if self.coupon:
    #         return (self.coupon.discount / Decimal('100')) \
    #                * self.get_total_price()
    #
    #     return Decimal('0')

    # def get_total_price_after_discount(self):
    #     return self.get_total_price() - self.get_discount()