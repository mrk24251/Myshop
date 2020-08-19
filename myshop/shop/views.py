from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from orders.models import OrderItem
from cart.forms import CartAddProductForm
from compare.forms import CompareAddProductForm
from .recommender import Recommender
import redis
from django.conf import settings
from django.http import HttpResponseRedirect

# connect to redis
r = redis.StrictRedis(host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB)

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        language = request.LANGUAGE_CODE
        category = get_object_or_404(Category,translations__language_code=language,translations__slug=category_slug)
        products = products.filter(category=category)
    return render(request,
        'shop/product/list.html',
        {'category': category,
        'categories': categories,
        'products': products})

def landing_page(request):
    if not request.session.has_key('currency'):
        request.session['currency']= settings.DEFAULT_CURRENCY

    products = Product.objects.filter(available=True)[:12]
    # return Post.published.annotate(
    #     total_comments=Count('comments')
    # ).order_by('-total_comments')[:count]
    category_list = Category.objects.all()
    popular_categories = r.zrange('category',0, -1, desc=True)[:6]

    popular_categories_ids = [int(id) for id in popular_categories]
    # get suggested products and sort by order of appearance
    popular_categories1 = list(Category.objects.filter(id__in=popular_categories_ids))
    popular_categories1.sort(key=lambda x: popular_categories_ids.index(x.id))

    hot_deals = Product.objects.filter(HotDeal=True)[:12]

    cart_product_form = CartAddProductForm()
    compare_product_form = CompareAddProductForm()

    return render(request,
        'shop/product/landingPage.html',
        {'products': products,
         'popular_categories':popular_categories1,
         'category_list':category_list,
         'hot_deal':hot_deals,
         'cart_product_form': cart_product_form,
         'compare_product_form': compare_product_form,
         })


def product_detail(request, id, slug):
    language = request.LANGUAGE_CODE
    product = get_object_or_404(Product,
        id=id,
        available=True,
        translations__language_code=language,
        translations__slug=slug,)
    compare_product_form = CompareAddProductForm()
    cart_product_form = CartAddProductForm()

    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)

    return render(request,
        'shop/product/detail.html',
        {'product': product,
         'compare_product_form': compare_product_form,
         'recommended_products': recommended_products})

def selectcurrency(request):

    lasturl = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        request.session['currency'] = request.POST['currency']

    return HttpResponseRedirect(lasturl)
