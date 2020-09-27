from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from shop import views

urlpatterns = [
    path('selectcurrency', views.selectcurrency, name='selectcurrency'),
]

urlpatterns += i18n_patterns(
    path('currencies/', include('currencies.urls')),
    path(_('admin/'), admin.site.urls),
    path('rosetta/', include('rosetta.urls')),
    path(_('list/cart/'), include('cart.urls', namespace='cart')),
    path(_('list/compare/'), include('compare.urls', namespace='compare')),
    path(_('orders/'), include('orders.urls', namespace='orders')),
    path(_(('payment/')), include('payment.urls', namespace='payment')),
    path(_(('subscribtion/')), include('email_subscription.urls', namespace='subscription')),
    path(_('coupons/'), include('coupons.urls', namespace='coupons')),
    path('', include('shop.urls', namespace='shop')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT)
