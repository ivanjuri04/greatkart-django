from django.contrib import admin
from .models import Cart,CartItem

# Register your models here.
class CartAdmin(admin.ModelAdmin):
    list_display=('cart_id','added_date')
    list_filter=['added_date']
    
    
class CartItemAdmin(admin.ModelAdmin):
    list_display=('product','quantity','cart','is_active','user')
      


admin.site.register(Cart,CartAdmin)
admin.site.register(CartItem,CartItemAdmin)


