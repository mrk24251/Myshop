from django.urls import path
from django.conf.urls import url
from . import views
from django.utils.translation import gettext_lazy as _

app_name = 'payment'

urlpatterns = [
    path(_('process/'), views.payment_process, name='process'),
    path(_('done/'), views.payment_done, name='done'),
    path(_('canceled/'), views.payment_canceled, name='canceled'),
    url(r'^request/$', views.send_request, name='request'),
    url(r'^verify/$', views.verify, name='verify'),
]