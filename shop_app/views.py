from django.shortcuts import render,redirect,HttpResponse
from . models import *
from django.contrib import messages
from shop_app.form import CustomUserForm
from django.contrib.auth import authenticate,login,logout
from django.http import  JsonResponse
import json


# Create your views here.
def index(request):
    products=Product.objects.filter(trending=1)
    return render(request, 'index.html',{"products":products})

def register(request):
    form=CustomUserForm()
    if request.method=='POST':
      form=CustomUserForm(request.POST)
      if form.is_valid():
        form.save()
        messages.success(request,"Registration Success You can Login Now..!")
        return redirect('/login')
    return render(request, 'register.html',{'form':form})

def login_page(request): 
    if request.user.is_authenticated:
      return redirect("/")
    else:
      if request.method=='POST':
        name=request.POST.get('username')
        pwd=request.POST.get('password')
        user=authenticate(request,username=name,password=pwd)
        if user is not None:
          login(request,user)
          messages.success(request,"Logged in Successfully")
          return redirect("/")
        else:
          messages.error(request,"Invalid User Name or Password")
          return redirect("/login")
      return render(request,'login.html')

def logout_page(request):
  if request.user.is_authenticated:
    logout(request)
    messages.success(request,"Logged out Successfully")
  return redirect("/")


def collections(request):
    category=Category.objects.filter(status=0)
    context={'category':category}
    return render(request, 'collections.html',context)

def collectionsview(request,name):
  if(Category.objects.filter(name=name,status=0)):
      products=Product.objects.filter(category__name=name)
      return render(request,"pindex.html",{"products":products,"category_name":name})
  else:
    messages.warning(request,"No Such Catagory Found")
    return redirect('collections')

def product_details(request,cname,pname):
    if(Category.objects.filter(name=cname,status=0)):
      if(Product.objects.filter(name=pname,status=0)):
        products=Product.objects.filter(name=pname,status=0).first()
        return render(request,"product_details.html",{"products":products})
      else:
        messages.error(request,"No Such Produtct Found")
        return redirect('collections')
    else:
      messages.error(request,"No Such Catagory Found")
      return redirect('collections')
    
def add_to_cart(request):
  if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)#load the json data that we passed form the html to data
      product_qty=data['product_qty']#get the product quantity
      product_id=data['pid']#get the product id
     
      product_status=Product.objects.get(id=product_id)#check whether product is available
      if product_status:#if available
        if Cart.objects.filter(user=request.user.id,product_id=product_id):
          #check whether the same user added it already
          return JsonResponse({'status':'Product Already in Cart'}, status=200)
        else:
          if product_status.quantity>=product_qty:#check the requested quanity availbale or not
            Cart.objects.create(user=request.user,product_id=product_id,product_qty=product_qty)
            return JsonResponse({'status':'Product Added to Cart'}, status=200)
          else:
            return JsonResponse({'status':'Product Stock Not Available'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Cart'}, status=200)
  else:
    return JsonResponse({'status':'Invalid Access'}, status=200)
  
def cart_page(request):
  if request.user.is_authenticated:
    cart=Cart.objects.filter(user=request.user)
    return render(request,"cart.html",{"cart":cart})
  else:
    return redirect("/")  
  
def remove_cart(request,cid):
  cartitem=Cart.objects.get(id=cid)
  cartitem.delete()
  return redirect("/cart")  

def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)
  

def favviewpage(request):
  if request.user.is_authenticated:
    fav=Favourite.objects.filter(user=request.user)
    return render(request,"fav.html",{"fav":fav})
  else:
    return redirect("/")  
  
def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviewpage")

def checkout(request):
  if request.user.is_authenticated:
    cart=Cart.objects.filter(user=request.user)
    return render(request,"checkout.html",{"cart":cart})
  else:
    return redirect("/")  
 

def deletekart(request):
  cartitem=Cart.objects.all()
  cartitem.delete()
  return redirect("/cart") 

