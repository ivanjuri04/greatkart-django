from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import RegistrationForm
from  .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from carts.models import Cart
from carts.views import _cart_id
from carts.models import CartItem
import requests



# Create your views here.
def register(request):
    context = {}
    if request.method == "POST":
        form=RegistrationForm(request.POST)

        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            phone_number=form.cleaned_data['phone_number']
            username=email.split("@")[0]

            user  = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            user.phone_number=phone_number  
            user.save()
            messages.success(request,'Registration successful')
            return redirect('register')
        else:
            form=RegistrationForm()
        context={'form':form,
             }
    return render(request,'register.html',context)

def login(request):
    if request.method == "POST":
        email=request.POST['email']
        password=request.POST['password']

        user=auth.authenticate(email=email,password=password) 

        if user is not None:
            try:
                
                cart=Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exist=CartItem.objects.filter(cart=cart).exists()
                
                if is_cart_item_exist:
                    cart_item=CartItem.objects.filter(cart=cart)
                    
                    product_variation = []
                    for item in cart_item: #getting product variation by cart_id
                        variation=item.variations.all()
                        product_variation.append(list(variation))

                    #get the cart items from the user to aces his product variation
                    cart_item=CartItem.objects.filter(user=user)
                    ex_var_list=[]
                    id=[]
                    for item in cart_item:
                         existing_variation=item.variations.all() #uzima iz baze
                         ex_var_list.append(list(existing_variation)) ##existing variation list
                         id.append(item.id)  

                   # product_variation= [1,2,3,4,6]  primjer da trazi ve jednake varijacije
                   # ex_var_list=[4.6.3.5]
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index=ex_var_list.index(pr)
                            item_id=id[index]     
                            item=CartItem.objects.get(id=item_id)
                            item.quantity+=1
                            item.user=user
                            item.save()
                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user=user
                                item.save()

                    #for item in cart_item:
                     #   item.user =user   
                      #  item.save() 
        
            except:
                
                pass


            auth.login(request,user)
            messages.success(request,'You are now logged in')
            url=request.META.get('HTTP_REFERER')
            try:
                query=requests.utils.urlparse(url).query
                #print('query-->',query) ##query--> next=/cart/checkout/
                params=dict(x.split('=') for x in query.split('&')) ##{'next': '/cart/checkout/'}
                #print('parms-->' , params)
                if 'next' in params :
                    nextPage=params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard') 
            
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('login')       

    return render(request,'login.html')

@login_required(login_url='login')
def logout(request):
    
    auth.logout(request)
    messages.success(request, 'You are logged out')
    return redirect('login')
    
@login_required(login_url='login')
def dashboard(request):
     return render(request,'dashboard.html')