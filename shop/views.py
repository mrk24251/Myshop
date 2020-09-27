from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from orders.models import OrderItem
from cart.forms import CartAddProductForm
from compare.forms import CompareAddProductForm
from .recommender import Recommender
import redis
from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger

# connect to redis
r = redis.StrictRedis(host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD)

def product_list(request, slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    products1 = Product.objects.filter(available=True)
    if slug:
        language = request.LANGUAGE_CODE
        category = get_object_or_404(Category,translations__language_code=language,translations__slug=slug)
        products = products.filter(category=category)
        products1 = products.filter(category=category)

    cart_product_form = CartAddProductForm()
    compare_product_form = CompareAddProductForm()

    paginator = Paginator(products, 16)  # 3 posts in each page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
    # If page is not an integer deliver the first page
        products = paginator.page(1)
    except EmptyPage:
    # If page is out of range deliver last page of results
        products = paginator.page(paginator.num_pages)

    return render(request,
        'shop/product/list.html',
        {'category': category,
        'categories': categories,
        'page': page,
        'products': products,
        'products1': products1,
        'cart_product_form': cart_product_form,
        'compare_product_form': compare_product_form,
    })

def landing_page(request):
    if not request.session.has_key('currency'):
        request.session['currency']= settings.DEFAULT_CURRENCY

    products = Product.objects.filter(available=True)[:12]
    # return Post.published.annotate(
    #     total_comments=Count('comments')
    # ).order_by('-total_comments')[:count]

    category_list = Category.objects.all()
    popular_categories = r.zrange('category',0, -1, desc=True)[:6]
    popular_products = r.zrange('product', 0, -1, desc=True)[:12]

    popular_categories_ids = [int(id) for id in popular_categories]
    popular_products_ids = [int(id) for id in popular_products]

    # get suggested products and sort by order of appearance
    popular_categories1 = list(Category.objects.filter(id__in=popular_categories_ids))
    popular_categories1.sort(key=lambda x: popular_categories_ids.index(x.id))

    popular_products1 = list(Product.objects.filter(id__in=popular_products_ids))
    popular_products1.sort(key=lambda x: popular_products_ids.index(x.id))

    hot_deals = Product.objects.filter(HotDeal=True)[:12]

    cart_product_form = CartAddProductForm()
    compare_product_form = CompareAddProductForm()

    return render(request,
        'shop/product/landingPage.html',
        {'products': products,
         'popular_categories':popular_categories1,
         'popular_products':popular_products1,
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

    products = Product.objects.filter(available=True)
    category_id = product.category.id
    category = get_object_or_404(Category, id=category_id)
    same_category = products.filter(category=category).exclude(id=id)

    compare_product_form = CompareAddProductForm()

    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)

    return render(request,
        'shop/product/detail.html',
        {'product': product,
         'compare_product_form': compare_product_form,
         'recommended_products': recommended_products,
         'same_category': same_category,
         })

def selectcurrency(request):

    lasturl = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        request.session['currency'] = request.POST['currency']

    return HttpResponseRedirect(lasturl)
