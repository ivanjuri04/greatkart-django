from django.urls import path
from . import views





urlpatterns = [
    path('register/',views.register,name="register"),
    path('login/',views.login,name="login"),
    path('logout/',views.logout,name="logout"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('',views.dashboard,name="dashboard"), ##da i bez extenzije dashboard ude u deshboard sa samo accounts upisanin u url
    path('my_orders/',views.my_orders,name="my_orders"),
    path('edit_profile/',views.edit_profile,name="edit_profile"),
    path('change_password/',views.change_password,name="change_password"),
    path('order_detail/<int:order_id>/',views.order_detail,name="order_detail"),    
    



    
    
]