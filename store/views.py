from django.forms import SlugField
from django.shortcuts import render,get_object_or_404
from . import views
from .models import Product,Category,ProductGallery
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.http import HttpResponse
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from django.db.models import Q ,Min ,Max



# Create your views here.
def store(request,category_slug=None):
    categories=None
    products=None
    if category_slug != None:
        categories=get_object_or_404(Category	,slug=category_slug)
        products=Product.objects.filter(category=categories,is_availbile=True)
        paginator=Paginator(products,2)
        page=request.GET.get('page')
        paged_product=paginator.get_page(page)
        product_count=products.count()
    else:
        products=Product.objects.all().filter(is_availbile=True).order_by('id') 
        paginator=Paginator(products,4)
        page=request.GET.get('page')
        paged_product=paginator.get_page(page)
        product_count=products.count()   
    MinMaxPrice=Product.objects.aggregate(Min('price'),Max('price'))#da maknen ovo nebi bilo plachoder price


    context={ 
        'products':paged_product,
        'product_count':product_count,
        'MinMaxPrice':MinMaxPrice,
    }
    return render (request,'store.html',context)







def product_detail(request,category_slug,product_slug):
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
       

    except Exception as e:
        raise e
    
    ##get the product gallery
    product_gallery=ProductGallery.objects.filter(product_id=single_product.id)
    
    context={ 
        
        'single_product':single_product,
        'in_cart':in_cart,
        'product_gallery':product_gallery,
    }

    return render(request,'product_detail.html',context)

def search(request):
    if 'keyword' in request.GET:
        keyword=request.GET['keyword']
        if keyword :
            products=Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count=products.count()
            context={
                'products':products,
                'product_count':product_count
            }
    return render(request,'store.html',context)


def price(request):
    if 'max_price' and 'min_price' in request.GET:
        max=request.GET['max_price']
        min=request.GET['min_price']
        if max and min:
            products = Product.objects.filter(price__gte=min, price__lte=max)

        context={
                'products':products,
            
            }
           
    return render(request,'store.html',context)

