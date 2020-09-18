import braintree
from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Order
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import weasyprint
from io import BytesIO
from django.db.models import F
import redis
from shop.models import Product
# -*- coding: utf-8 -*-
# Github.com/Rasooll
from django.http import HttpResponse
from django.shortcuts import redirect
from zeep import Client


# connect to redis
r = redis.StrictRedis(host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB)
# for test 'df04b34a-c7da-11e8-99d0-005056a205be'
MERCHANT = 'df04b34a-c7da-11e8-99d0-005056a205be'
client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
email = 'email@example.com'  # Optional
mobile = '09123456789'  # Optional
CallbackURL = 'http://127.0.0.1:8000/payment/verify/' # Important: need to edit for realy server.

def send_request(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    amount1 ='{:.9f}'.format(order.get_total_cost()* 10000)

    result = client.service.PaymentRequest(MERCHANT, amount1, description, email, mobile, CallbackURL)
    if result.Status == 100:
        return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        return HttpResponse('Error code: ' + str(result.Status))

def verify(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.GET.get('Status') == 'OK':
        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], amount)
        if result.Status == 100:
            for item in order.items.all():
                pp = item.product
                pp.HotDealAmount = F('HotDealAmount') - item.quantity
                pp.save()

            order.paid = True
            # store the unique transaction id
            order.braintree_id = result.transaction.id
            order.save()
            # create invoice e-mail
            subject = 'My Shop - Invoice no. {}'.format(order.id)
            message = 'Please, find attached the invoice for your recent purchase.'
            email = EmailMessage(subject,
                                 message,
                                 'mrkarami24251@gmail.com',
                                 [order.email])

            html = render_to_string('orders/order/pdf.html', {'order':order})
            out = BytesIO()
            stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
            weasyprint.HTML(string=html).write_pdf(out,stylesheets=stylesheets)
            # attach PDF file
            email.attach('order_{}.pdf'.format(order.id),
                         out.getvalue(),
                         'application/pdf')
            # send e-mail
            email.send()

            return redirect('payment:done')
            # return HttpResponse('Transaction success.\nRefID: ' + str(result.RefID))
        elif result.Status == 101:
            return redirect('payment:canceled')
        else:
            return redirect('payment:canceled')
    else:
        return redirect('payment:canceled')


def payment_process(request):

    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # retrieve nonce
        nonce = request.POST.get('payment_method_nonce', None)
        # create and submit transaction
        result = braintree.Transaction.sale({
            'amount': '{:.2f}'.format(order.get_total_cost()),
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })

        if result.is_success:
            # mark the order as paid
            for item in order.items.all():
                pp = item.product
                pp.HotDealAmount = F('HotDealAmount') - item.quantity
                pp.save()

            order.paid = True
            # store the unique transaction id
            order.braintree_id = result.transaction.id
            order.save()
            # create invoice e-mail
            subject = 'My Shop - Invoice no. {}'.format(order.id)
            message = 'Please, find attached the invoice for your recent purchase.'
            email = EmailMessage(subject,
                                 message,
                                 'mrkarami24251@gmail.com',
                                 [order.email])

            html = render_to_string('orders/order/pdf.html', {'order':order})
            out = BytesIO()
            stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
            weasyprint.HTML(string=html).write_pdf(out,stylesheets=stylesheets)
            # attach PDF file
            email.attach('order_{}.pdf'.format(order.id),
                         out.getvalue(),
                         'application/pdf')
            # send e-mail
            email.send()

            return redirect('payment:done')
        else:
            return redirect('payment:canceled')
    else:
        # generate token
        client_token = braintree.ClientToken.generate()
        return render(request,
            'payment/process.html',
            {'order': order,
            'client_token': client_token})

def payment_done(request):
    return render(request, 'payment/done.html')

def payment_canceled(request):
    return render(request, 'payment/canceled.html')