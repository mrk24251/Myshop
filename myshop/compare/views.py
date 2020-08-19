from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from shop.models import Product
from .compare import Compare
from .forms import CompareAddProductForm

@require_POST
def compare_add(request, product_id):
    compare = Compare(request)
    product = get_object_or_404(Product, id=product_id)
    form = CompareAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        compare.add(product=product)

    return redirect('compare:compare_detail')

def compare_remove(request, product_id):
    compare = Compare(request)
    product = get_object_or_404(Product, id=product_id)
    compare.remove(product)
    return redirect('compare:compare_detail')

def compare_detail(request):
    compare = Compare(request)
    return render(request, 'compare/detail.html', {'compare': compare})