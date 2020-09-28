from django.shortcuts import render,redirect
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from shop.models import Product
from .tasks import order_created
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .models import Order
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint
import redis
from shop.recommender import Recommender
from decimal import Decimal

# connect to redis
r = redis.StrictRedis(host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD)

def order_create(request):
    cart = Cart(request)
    rr = Recommender()
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount

            order.save()
            recommending= []
            for item in cart:
                price_after_discount = item['total_price_after_discount']
                recommending.append(Product.objects.get(id=item['product'].id))
                category_id=item['product'].category.id
                r.zincrby('category',
                          1,category_id)

                product_id = item['product'].id

                r.zincrby('product',
                          1, product_id)

                OrderItem.objects.create(order=order,
                    product=item['product'],
                    price=price_after_discount,
                    quantity=item['quantity'])

                # pp=item['product']
                # pp.HotDealAmount = F('HotDealAmount') - item['quantity']
                # pp.save()

            rr.products_bought(recommending)
            # clear the cart
            cart.clear()
            # launch asynchronous task
            # order_created.delay(order.id)
            # set the order in the session
            request.session['order_id'] = order.id
            # redirect for payment
            if request.session['currency'] == "IRR":
                return redirect(reverse('payment:request'))
            else:
                return redirect(reverse('payment:process'))

    else:
        form = OrderCreateForm()
    return render(request,
    'orders/order/create.html',
    {'cart': cart, 'form': form})

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
        'admin/orders/order/detail.html',
        {'order': order})

@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    html = render_to_string('orders/order/pdf.html',
        {'order': order})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=\
        "order_{}.pdf"'.format(order.id)

    weasyprint.HTML(string=html).write_pdf(response,
        stylesheets=[weasyprint.CSS(
            settings.STATIC_ROOT + 'css/pdf.css')])

    return response