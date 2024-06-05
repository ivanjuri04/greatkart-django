from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .forms import RegistrationForm,UserProfileForm,UserForm
from  .models import Account,UserProfile
from orders.models import Order,OrderProduct	
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
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
            return redirect('login')
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
                params=dict(x.split('=') for x in query.split('&')) ##{'next': '/cart/checkout/'} da se vrati os stranuce di je bia
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
     orders=Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)##moze i user=request.user
     orders_count=orders.count()
     userprofile=UserProfile.objects.get(user=request.user)
     context={
         'orders_count':orders_count,
         'userprofile':userprofile,
         'orders':orders,
     }
     return render(request,'dashboard.html',context)

def my_orders(request):
    orders=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context={
        'orders':orders
    }
    return render(request,'my_orders.html',context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user) ##uzima profil il vraca 404 error
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)##sa instance ne stvaramo novi nego updejtamo postojeci
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)##jer uplodam sliku je .FILES
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
        
    return render(request, 'change_password.html')

@login_required(login_url='login')
def order_detail(request,order_id):  ##automatski uzima order_id i stavlja ga u link
    order_detail=OrderProduct.objects.filter(order__order_number=order_id)  ##order i order_number
    order=Order.objects.get(order_number=order_id)
    subtotal=0
    for i in order_detail:
        subtotal+=i.product_price  * i.quantity

    context={
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal,
    }
    return render (request,'order_detail.html',context)