from django.urls import path, re_path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('list/', views.product_list, name='product_list'),
    re_path(r'^(?P<slug>[\w-]+)/$', views.product_list,
        name='product_list_by_category'),
    re_path(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/$', views.product_detail,
        name='product_detail'),
]