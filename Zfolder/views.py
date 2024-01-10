from django.shortcuts import render
from store.models import Product

def home(request):
    products=Product.objects.all().filter(is_availbile=True)
    context={ 
        'products':products,
    }
    return render(request, "home.html", context)





                

