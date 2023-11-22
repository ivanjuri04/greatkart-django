from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import request


def home(request):

    return render(request,"webshop/home.html")


# Create your views here.
