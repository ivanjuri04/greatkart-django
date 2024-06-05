from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order
from .models import TaxSettings
from .models import Payment
from .models import OrderProduct
from store.models import Product
import datetime
import json
# Create your views here.

def  place_order(request):
    tax_settings = TaxSettings.objects.first()
    if tax_settings:
            tax_percentage = float(tax_settings.tax_percentage)
    current_user=request.user
    cart_items=CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count <= 0  :
        return redirect('store')
    
   
    tax=0
    total=0
    quantity=0

    for cart_item in cart_items:
        total+=(cart_item.product.price * cart_item.quantity)
        quantity+=cart_item.quantity

    tax=((tax_percentage/100)*total)
    

    
    if request.method == 'POST':
        form=OrderForm(request.POST)
        
        if form.is_valid(): 
             #ako je valid spremi sve inf
            data=Order()
            data.user=current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.zip_code = form.cleaned_data['zip_code']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total=total
            data.tax=tax
            data.ip=request.META.get('REMOTE_ADDR')
            data.save()

        


            #generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number=current_date+str(data.id)
            data.order_number=order_number
            data.save()
            order=Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            context={
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                
            }
            
            return render(request,'payments.html',context)
    else:
            
        return redirect('home')
            

    return render(request,'place_order.html')

def payments(request):
    body=json.loads(request.body)
    order=Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])
    #inf iz placanja saljemo u backend
    payment=Payment(
        user=request.user,
        payment_id= body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
        

    )
    payment.save()

    order.payment=payment
    order.is_ordered=True
    order.save()

    #move cart items to Order Product table 
    cart_items=CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct=OrderProduct() ##stvaramo orderproduct
        orderproduct.order_id=order.id ## imamo vec orderid i punimo orderproduct
        orderproduct.payment=payment
        orderproduct.user_id=request.user.id
        orderproduct.product_id=item.product_id
        orderproduct.quantity=item.quantity
        orderproduct.product_price=item.product.price
        orderproduct.ordered=True
        orderproduct.save()   #za manytomany field npr varitation prvo triba spremit i onda upisat vridnost

        cart_item=CartItem.objects.get(id=item.id)  ##uzime cart item po item id
        product_variations=cart_item.variations.all()#uzima sve varijacije u tome cart itemu
        orderproduct=OrderProduct.objects.get(id=orderproduct.id) #orderproduct uzima sve sa tin orderproduct id npr ui narudbi su 2 proizvoda i imaj orderproductid 3
        orderproduct.variations.set(product_variations)
        orderproduct.save()



        #Reduce quantity of sold products
        product=Product.objects.get(id=item.product_id)
        product.stock-=item.quantity
        product.save()

    #Clear the cart
    CartItem.objects.filter(user=request.user).delete()    

    #Send ordernumber and transID back to SendData method via JsonResponse
    data={
        'order_number':order.order_number,
        'transID':payment.payment_id,


    }

        
    
    return JsonResponse(data)


def order_complete(request):
    order_number=request.GET.get('order_number')
    transID=request.GET.get('payment_id') ##sad priko order_number i tranksID printsmo podatke kupnje

    payment=Payment.objects.get(payment_id=transID)

    try:
        order=Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_products=OrderProduct.objects.filter(order_id=order.id)

        subtotal=0
        for i in ordered_products:
            subtotal+=i.product_price*i.quantity

        context={
            'order':order,
            'ordered_products':ordered_products,
            'order_number':order.order_number,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal
        }

        return render(request,'order_complete.html',context)
    
    except (Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('home')
