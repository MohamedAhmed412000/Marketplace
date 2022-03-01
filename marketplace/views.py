from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from Ecommerce.settings import MEDIA_ROOT
from .models import Cart, Ownership, Product, Account, Market
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django import forms
import os

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    else:
        request.session['back'] = 'index'
        products = Product.objects.exclude(user= request.user.id).all().filter(quantity__range= (1,100)).order_by("-recommend")
        my_products = Product.objects.filter(user= request.user.id).filter(quantity__range= (1,100)).order_by("-recommend")
        return render(request, "marketplace/index.html", {
            "products": products,
            "myproducts": my_products,
            "id": request.user.id
        })

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "marketplace/login.html", {
                "message": "Invalid credentials",
                "login": True
            })
    else:
        return render(request, "marketplace/login.html", {
            "login": True
        })

@csrf_exempt
def register_view(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm = request.POST["confirm"]
        if password != confirm:
            return render(request, "marketplace/login.html", {
                "message": "Passwords must match",
                "login": False
            })
        try:
            user = Account.objects.create_user(request.POST["email"], request.POST["username"], password)
            user.save()
            login(request, user, backend="marketplace.backends.CaseInsensitiveModelBackend")
            return HttpResponseRedirect(reverse("index"))
        except:
            return render(request, "marketplace/login.html", {
                "message": "Email or Username already taken"
            })
    else: 
        return render(request, "marketplace/login.html", {
            "login": False
        })

def logout_view(request):
    logout(request)
    return render(request, "marketplace/login.html", {
        "login": True
    })

@login_required
def cart(request, id):
    if request.user.id != int(id):
        return HttpResponseRedirect(reverse("index"))
    request.session['back'] = 'cart'
    user = Account.objects.get(pk= id)
    cart = Cart.objects.filter(user= user)
    sum = tax = 0
    for i in cart:
        sum += float(i.product.price)
        tax = 30
    return render(request, "marketplace/cart.html", {
        "items": cart,
        "id": id,
        "sum": sum,
        "tax": tax,
        "fullSum": sum + tax,
        "message": ""
    })

@csrf_exempt
def cartConfirm(request, id):
    if request.method == "POST":
        user = Account.objects.get(pk= id)
        quantities = request.POST.getlist('quantity')
        carts = Cart.objects.filter(user= user)
        sum = 0
        tax = 30
        for cart in carts:
            sum += float(cart.product.price)
        # Check right amount of quantities
        for i in range(len(carts)):
            if int(quantities[i]) > int(carts[i].product.quantity):
                return render(request, "marketplace/cart.html", {
                    "message": f'Max. num of quantities for "{carts[i].product}" is {carts[i].product.quantity}.',
                    "items": carts,
                    "id": id,
                    "sum": sum,
                    "tax": tax,
                    "fullSum": sum + tax
                })
        # Check valid user balance for this opration
        if user.balance < (sum + tax):
            return render(request, "marketplace/cart.html", {
                "message": "You don't have enough balance for this operation.",
                "items": carts,
                "id": id,
                "sum": sum,
                "tax": tax,
                "fullSum": sum + tax
            })
        user.balance -= tax
        request.session["order_id"] = []
        for i in range(len(carts)):
            # Money transfer
            user.balance -= carts[i].product.price
            carts[i].product.user.balance += carts[i].product.price
            user.save()
            carts[i].product.user.save()
            # Make Transfer History
            transfer = Ownership.objects.create(
                seller = carts[i].product.user,
                buyer = user,
                product = carts[i].product,
                quantity = quantities[i]
            )
            transfer.save()
            # Reduce product quantity
            carts[i].product.quantity -= int(quantities[i])
            carts[i].product.save()
            # Remove item from Cart
            carts[i].delete()
            request.session["order_id"].append(str(transfer.id))
        return redirect(reverse('payment:process'))
    return HttpResponseRedirect(reverse("cart", args=(id,)))

def cartRemove(request, id, cid):
    Cart.objects.filter(pk= cid).delete()
    return HttpResponseRedirect(reverse("cart", args=(id,)))

def cartAdd(request, id, pid):
    try:
        user = Account.objects.get(pk= id)
        product = Product.objects.get(pk= pid)
        cart = Cart.objects.create(user= user, product= product, quantity= 1)
        cart.save()  
    except:
        pass
    # return HttpResponseRedirect(reverse("cart", args=(id,)))
    return HttpResponseRedirect(reverse("index"))
    
@login_required
def market(request, id):
    perm = True
    if int(id) != request.user.id:
        perm = False
    request.session['back'] = 'market'
    user = Account.objects.get(pk= id)
    mProducts = Product.objects.filter(user= user, quantity__range= (1,100))
    otherProducts = Market.objects.filter(user= user)
    oProducts = []
    for market in otherProducts:
        if market.product.quantity > 0:
            oProducts.append(market)
    return render(request, "marketplace/market.html", {
        "id": id,
        "user": user,
        "mproducts": mProducts,
        "oproducts": oProducts,
        "flag": perm
    })

def marketAdd(request, id, pid):
    try:
        user = Account.objects.get(pk= id)
        product = Product.objects.get(pk= pid)
        market = Market.objects.create(user= user, product= product)
        market.save()
        product.recommend += 1
        product.save()
    except:
        pass
    # return HttpResponseRedirect(reverse("market", args=(id,)))
    return HttpResponseRedirect(reverse("index"))

def marketRemove(request, id, mid):
    market = Market.objects.get(pk= mid)
    product = market.product
    product.recommend -= 1
    product.save()
    market.delete()
    return HttpResponseRedirect(reverse("market", args=(id,)))

class ImageForm(forms.Form):
    image = forms.ImageField(label="Select an image", required=False)

@csrf_exempt
def addProduct(request, id):
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            user = Account.objects.get(pk= id)
            product = Product.objects.create(
                name = request.POST["name"],
                description = request.POST["description"],
                price = request.POST["price"],
                quantity = request.POST["quantity"],
                user = user,
                recommend = 0,
                category = request.POST["category"],
                image = request.FILES["image"]
            )
            product.save()
            return HttpResponseRedirect(reverse("market", args=(id,)))
    return render(request, "marketplace/add product.html", {
        "id": id,
        "form": ImageForm(),
        "Pimage": "default.jpg",
        "add": True
    })

def deleteProduct(request, id, pid):
    product = Product.objects.get(pk= pid)
    os.remove(MEDIA_ROOT + str(product.image))
    product.delete()
    return HttpResponseRedirect(reverse("market", args=(id,)))

@csrf_exempt
def editProduct(request, id, pid):
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            product = Product.objects.get(pk= pid)
            product.name = request.POST["name"]
            product.description = request.POST["description"]
            product.price = request.POST["price"]
            product.quantity = request.POST["quantity"]
            product.category = request.POST["category"]
            try:
                product.image = request.FILES["image"] if request.FILES["image"] != "" else product.image
            except:
                pass
            product.save()
        return HttpResponseRedirect(reverse("market", args=(id,)))
    else:
        product = Product.objects.get(pk= pid)
        options = {
            "1": "selected" if product.category == "Digital Devices" else "",
            "2": "selected" if product.category == "Clothes" else "",
            "3": "selected" if product.category == "Sport" else "",
            "4": "selected" if product.category == "Food" else "",
            "5": "selected" if product.category == "Home Devices" else "",
            "6": "selected" if product.category == "Other" else ""
        }
        return render(request, "marketplace/add product.html", {
            "id": id,
            "form": ImageForm(),
            "Pimage": str(product.image),
            "product": product,
            "options": options,
            "add": False
        })        

@login_required
def account(request, id):
    if request.user.id == int(id):
        request.session['back'] = 'account'
        user = Account.objects.get(pk= id)
        sProducts = Ownership.objects.filter(seller= user)
        pProducts = Ownership.objects.filter(buyer= user)
        return render(request, "marketplace/account.html", {
            "user": user,
            "sproduct": sProducts,
            "pproduct": pProducts
        })
    return HttpResponseRedirect(reverse('index'))

@login_required
@csrf_exempt
def search(request):
    if request.method == "POST":
        try:
            data = request.POST["data"]
            results = Product.objects.filter(Q(name__icontains = data), quantity__range= (1,100))
        except:
            categories = ["Digital Devices", "Clothes", "Sport", "Food", "Home Devices", "Other"]
            idx = int(request.POST["category"])
            data = categories[idx]
            results = Product.objects.filter(category= data, quantity__range= (1,100))
    request.session['back'] = 'search'
    return render(request, "marketplace/search.html", {
        "id": request.user.id,
        "data": data,
        "products": results
    })

def product(request, id):
    product = Product.objects.get(pk= id)
    transfer = Ownership.objects.filter(product= product).first()
    if transfer != None:
        product.user = transfer.buyer
    return render(request, "marketplace/product.html",{
        "product": product,
        "id": request.user.id
    })

def back(request, id):
    if request.session['back'] in ['index', 'search']:
        return HttpResponseRedirect(reverse(request.session['back']))
    return HttpResponseRedirect(reverse(request.session['back'], args=(id,)))

def help(request):
    return render(request, "marketplace/help.html")
