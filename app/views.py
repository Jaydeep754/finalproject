from django.shortcuts import render, redirect
from django.views import View
from .models import Product, Customer, Cart, Payment, DeliveryPerson, OrderPlaced, ProductReview, Complaint, CATEGORY_CHOICES
from .forms import *
import razorpay
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
# ...existing code...

@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def admin_send_notification(request):
    customers = Customer.objects.select_related('user').all()
    if request.method == 'POST':
        subject = request.POST.get('subject')
        reason = request.POST.get('reason')
        selected_ids = request.POST.getlist('customer_ids')
        if selected_ids:
            selected_customers = customers.filter(id__in=selected_ids)
            emails = [c.user.email for c in selected_customers if c.user.email]
        else:
            emails = [c.user.email for c in customers if c.user.email]
        from_email = settings.DEFAULT_FROM_EMAIL
        if emails:
            try:
                send_mail(subject, reason, from_email, emails)
                messages.success(request, f'Notification sent to {len(emails)} customer(s).')
            except Exception as e:
                messages.error(request, f'Error sending notification: {e}')
        else:
            messages.error(request, 'No customer emails found.')
        return render(request, 'admin_panel/send_notification.html', {'customers': customers})
    return render(request, 'admin_panel/send_notification.html', {'customers': customers})
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import datetime, timedelta

# For PDF Generation
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO

# displays no .of items in cart
def cart_num(request)->int:
    if request.user.is_authenticated:
        return  Cart.objects.filter(user=request.user).count()
    else:
        cart = request.session.get('cart', {})
        return len(cart)


# Create your views here.
def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try regular authentication first
        user = authenticate(request, username=email, password=password)
        
        # If regular auth fails, check Hardcoded Credentials
        if not user and email == 'sahilbatman234@gmail.com' and password == 'password':
            user = User.objects.filter(email=email).first()
            if not user:
                user = User.objects.create_user(username=email, email=email, password=password)
        
        if user is not None:
            login(request, user)
            
# Migrate session cart to DB
            session_cart = request.session.get('cart', {})
            if session_cart:
                for cart_key, item_data in session_cart.items():
                    try:
                        if isinstance(item_data, dict):
                            prod_id = item_data['product_id']
                            quantity = item_data['quantity']
                            size = item_data['size']
                            price = item_data['price']
                        else:
                            # Backward compatibility for old simple session cart
                            prod_id = cart_key
                            quantity = item_data
                            size = "500gm"
                            product = Product.objects.get(id=prod_id)
                            price = product.discounted_price

                        product = Product.objects.get(id=prod_id)
                        item, created = Cart.objects.get_or_create(user=user, product=product, size=size)
                        if not created:
                            item.quantity += quantity
                            item.save()
                        else:
                            item.quantity = quantity
                            item.price = price
                            item.save()
                    except Product.DoesNotExist:
                        continue
                del request.session['cart']
                
            messages.success(request, f"Welcome back. Access Granted.")
            if hasattr(user, 'deliveryperson'):
                return redirect('delivery-dashboard')
            return redirect('home')
        else:
            messages.error(request, "Invalid Credentials! Access Denied.")
            return render(request, 'login.html')
            
    return render(request, 'login.html')

def home(request):
    cartitem = cart_num(request)
    #
    return render(request, "index.html",locals())

def about(request):
    cartitem = cart_num(request)
    # 
    return render(request, "about.html",locals())

def contact(request):
    cartitem = cart_num(request)
    # 
    return render(request, "contact.html",locals())

class  CategoryView(View):
    def get(self, request, value):
        cartitem = cart_num(request)
        # Only show products that have an image
        product = Product.objects.filter(category = value).exclude(product_image='').order_by('-id')
        title = product.values('title').distinct()
        return render(request,"category.html",locals())
    
class CategoryTitle(View):
    def get(self, request, value):
        cartitem = cart_num(request)
        # Only show products that have an image
        product = Product.objects.filter(title = value).exclude(product_image='')
        if product.exists():
            title = Product.objects.filter(category = product[0].category).exclude(product_image='').values('title').distinct()
        else:
            title = []
        return render(request, "category.html", locals())
    

class ProductDetail(View):
    def get(self, request, pk):
        cartitem = cart_num(request)
        # 
        product = Product.objects.get(id = pk) 
        
        # Calculate Average Rating and get Reviews
        from django.db.models import Avg
        average_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        reviews = product.reviews.all().order_by('-created_at')
        review_form = ProductReviewForm()
        
        # Check if user can review (only if they bought and it's delivered)
        can_review = False
        if request.user.is_authenticated:
            can_review = OrderPlaced.objects.filter(user=request.user, product=product, status='Delivered').exists()
        
        # Determine size options
        if product.category in ['MK', 'LS', 'BS']:
            sizes = ['1L', '500ml', '2L']
        else:
            sizes = ['1kg', '500gm', '2kg']
        
        return render(request,'productdetail.html',locals())
    
class CustomerRegistrationView(View):
    def get(self, request):
        cartitem = cart_num(request)
        form = CustomerRegistrationForm()
        return render(request,"signup.html",locals())
    
    def post(self, request):
        cartitem = cart_num(request)
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            messages.warning(request,"Invalid data Inputs! ")
        return render(request,"signup.html",locals())

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        cartitem = cart_num(request)
        # 
        form = CustomerProfileForm()
        return render(request,'profile.html',locals())

    def post(self, request):
        cartitem = cart_num(request)
        # 
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode).save()
            
            return redirect('address')
        else:
            messages.warning(request,"Invalid data Inputs! ")
        return render(request,'profile.html',locals())

@login_required
def adress(request):
    cartitem = cart_num(request)
    # 
    add = Customer.objects.filter(user=request.user)
    return render(request,'address.html',locals())

@login_required
def delete_address(request,pk):
    Customer.objects.get(id=pk).delete()
    return redirect('address')
    
@method_decorator(login_required, name='dispatch')
class UpdateAddress(View):
    def get(self,request,pk):
        cartitem = cart_num(request)
        #
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request,'updateaddress.html',locals())
    
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Congratulations! Profile Updated Succesfully")
        else:
            messages.warning(request,"Invalid data Inputs! ")
        return redirect('address')
        
@login_required
def Logout(request):
     logout(request)
     return redirect('home')

def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('prod_id')
        quantity = int(request.POST.get('quantity', 1))
        size = request.POST.get('size', '500gm')
    else:
        product_id = request.GET.get('prod_id')
        quantity = int(request.GET.get('quantity', 1))
        size = request.GET.get('size', '500gm')
    product = Product.objects.get(id=product_id)
    
    # Baseline is 1kg/L = 1x price
    multiplier = 1.0
    if '500gm' in size or '500ml' in size:
        multiplier = 0.5
    elif '2kg' in size or '2L' in size:
        multiplier = 2.0
        
    price = product.discounted_price * multiplier

    if request.user.is_authenticated:
        user = request.user
        # Check if item with SAME SIZE exists in cart
        item = Cart.objects.filter(product=product, user=user, size=size).first()
        
        # Check if quantity requested exceeds available stock
        current_cart_qty = item.quantity if item else 0
        if current_cart_qty + quantity > product.quantity:
            messages.warning(request, f"Cannot add. Only {product.quantity} unit(s) of {product.title} available in stock.")
            return redirect('product-detail', pk=product_id)
            
        if item:
            if item.quantity + quantity > 10:
                item.quantity = 10
                item.save()
                messages.warning(request, f"Maximum 10 quantities allowed for {product.title} ({size}).")
            else:
                item.quantity += quantity
                item.save()
                messages.success(request, f"Updated {product.title} ({size}) quantity.")
        else:
            if quantity > 10:
                quantity = 10
                messages.warning(request, f"Maximum 10 quantities allowed for {product.title} ({size}).")
            else:
                messages.success(request, f"Added {product.title} ({size}) to your collection.")
            Cart(user=user, product=product, quantity=quantity, size=size, price=price).save()
    else:
        # Session based cart for visitors
        cart = request.session.get('cart', {})
        cart_key = f"{product_id}_{size}"
        
        # Check if quantity requested exceeds available stock
        current_cart_qty = cart[cart_key]['quantity'] if cart_key in cart else 0
        if current_cart_qty + quantity > product.quantity:
            messages.warning(request, f"Cannot add. Only {product.quantity} unit(s) of {product.title} available in stock.")
            return redirect('product-detail', pk=product_id)
            
        if cart_key in cart:
            if cart[cart_key]['quantity'] + quantity > 10:
                cart[cart_key]['quantity'] = 10
                messages.warning(request, f"Maximum 10 quantities allowed for {product.title} ({size}).")
            else:
                cart[cart_key]['quantity'] += quantity
                messages.success(request, f"Added {product.title} ({size}) to your guest collection.")
        else:
            if quantity > 10:
                quantity = 10
                messages.warning(request, f"Maximum 10 quantities allowed for {product.title} ({size}).")
            else:
                messages.success(request, f"Added {product.title} ({size}) to your guest collection.")
            cart[cart_key] = {
                'product_id': product_id,
                'quantity': quantity,
                'size': size,
                'price': price
            }
        request.session['cart'] = cart
        
    # Check for buy_now in both POST and GET for compatibility
    buy_now = request.POST.get('buy_now') or request.GET.get('buy_now')
    if buy_now:
        return redirect('checkout')
        
    return redirect('showcart')


def showcart(request):
    cartitem = cart_num(request)
    amount = 0
    cart = []
    
    if request.user.is_authenticated:
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        for c in cart_items:
            amount += c.quantity * c.price
            cart.append({
                'product': c.product,
                'quantity': c.quantity,
                'size': c.size,
                'price': c.price,
                'total_cost': c.quantity * c.price
            })
    else:
        # Session-based cart for guests
        session_cart = request.session.get('cart', {})
        for cart_key, item_data in session_cart.items():
            try:
                prod_id = item_data['product_id']
                quantity = item_data['quantity']
                size = item_data['size']
                price = item_data['price']
                product = Product.objects.get(id=prod_id)
                cart.append({
                    'product': product,
                    'quantity': quantity,
                    'size': size,
                    'price': price,
                    'total_cost': quantity * price
                })
                amount += quantity * price
            except Product.DoesNotExist:
                continue
                
    shipping_fee = 0 if amount >= 500 else (40 if amount > 0 else 0)
    totalamount = amount + shipping_fee
    login_required_popup = request.GET.get('login_required_popup')
    return render(request, 'cart.html', locals())

def pluscart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        size = request.GET.get('size', '500gm')
        quantity = 0
        amount = 0
        error_msg = ""
        
        if request.user.is_authenticated:
            c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user) & Q(size=size))
            if c.quantity < 10:
                if c.quantity + 1 > c.product.quantity:
                    error_msg = f"Only {c.product.quantity} unit(s) available in stock."
                else:
                    c.quantity += 1
                    c.save()
            else:
                error_msg = "Maximum 10 quantities allowed for a particular item."
            quantity = c.quantity
            cart_items = Cart.objects.filter(user=request.user)
            for p in cart_items:
                amount += p.total_cost
        else:
            cart = request.session.get('cart', {})
            cart_key = f"{prod_id}_{size}"
            if cart_key in cart:
                p = Product.objects.get(id=prod_id)
                if cart[cart_key]['quantity'] < 10:
                    if cart[cart_key]['quantity'] + 1 > p.quantity:
                        error_msg = f"Only {p.quantity} unit(s) available in stock."
                    else:
                        cart[cart_key]['quantity'] += 1
                        request.session['cart'] = cart
                else:
                    error_msg = "Maximum 10 quantities allowed for a particular item."
                quantity = cart[cart_key]['quantity']
            for ck, data in cart.items():
                if isinstance(data, dict):
                    amount += data['quantity'] * data['price']
                else:
                    p = Product.objects.get(id=ck)
                    amount += data * p.discounted_price
                
                
        shipping_fee = 0 if amount >= 500 else (40 if amount > 0 else 0)
        totalamount = amount + shipping_fee
        data = {
            'quantity': quantity,
            'amount': amount,
            'totalamount': totalamount,
            'shipping_fee': shipping_fee,
            'error': error_msg
        }
        return JsonResponse(data)
    
def minuscart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        size = request.GET.get('size', '500gm')
        quantity = 0
        amount = 0
        
        if request.user.is_authenticated:
            c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user) & Q(size=size))
            if c.quantity > 1:
                c.quantity -= 1
                c.save()
            quantity = c.quantity
            cart_items = Cart.objects.filter(user=request.user)
            for p in cart_items:
                amount += p.total_cost
        else:
            cart = request.session.get('cart', {})
            cart_key = f"{prod_id}_{size}"
            if cart_key in cart:
                if cart[cart_key]['quantity'] > 1:
                    cart[cart_key]['quantity'] -= 1
                request.session['cart'] = cart
                quantity = cart[cart_key]['quantity']
            for ck, data in cart.items():
                if isinstance(data, dict):
                    amount += data['quantity'] * data['price']
                else:
                    p = Product.objects.get(id=ck)
                    amount += data * p.discounted_price
                
                
        shipping_fee = 0 if amount >= 500 else (40 if amount > 0 else 0)
        totalamount = amount + shipping_fee
        data = {
            'quantity': quantity,
            'amount': amount,
            'totalamount': totalamount,
            'shipping_fee': shipping_fee
        }
        return JsonResponse(data)
    
def removecart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        size = request.GET.get('size', '500gm')
        amount = 0
        
        if request.user.is_authenticated:
            c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user) & Q(size=size))
            c.delete()
            cart_items = Cart.objects.filter(user=request.user)
            for p in cart_items:
                amount += p.total_cost
        else:
            cart = request.session.get('cart', {})
            cart_key = f"{prod_id}_{size}"
            if cart_key in cart:
                del cart[cart_key]
                request.session['cart'] = cart
            for ck, data in cart.items():
                if isinstance(data, dict):
                    amount += data['quantity'] * data['price']
                else:
                    p = Product.objects.get(id=ck)
                    amount += data * p.discounted_price
                
                
        shipping_fee = 0 if amount >= 500 else (40 if amount > 0 else 0)
        totalamount = amount + shipping_fee
        data = {
            'amount': amount,
            'totalamount': totalamount,
            'shipping_fee': shipping_fee
        }
        return JsonResponse(data)
      

class CheckoutView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            # If visitor tries to checkout, redirect to cart with popup flag
            return redirect('/cart/?login_required_popup=true')
            
        cartitem = cart_num(request)
        user = request.user
        add = Customer.objects.filter(user=user, city__iexact='Ahmedabad')
        if not add.exists():
            all_addresses = Customer.objects.filter(user=user)
            if all_addresses.exists():
                messages.warning(request, "Currently, we only deliver to Ahmedabad. We're coming soon to your city!")
            else:
                messages.warning(request, "Please add a shipping address in Ahmedabad to proceed.")
            return redirect('profile')
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            return redirect('showcart')
            
        # Validate that cart items don't exceed available stock
        for item in cart_items:
            if item.quantity > item.product.quantity:
                messages.error(request, f"Sorry, the requested quantity for {item.product.title} exceeds our available stock ({item.product.quantity} left). Please update your cart.")
                return redirect('showcart')
            
        famount = 0
        for p in cart_items:
            value = p.total_cost
            famount+= value
            
        shipping_fee = 0 if famount >= 500 else (40 if famount > 0 else 0)
        totalamount = famount + shipping_fee
        
        razoramount = int(totalamount * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID,settings.RAZOR_KEY_SECRET))
        data = { "amount": razoramount, "currency": "INR", "receipt": "order_rcptid_11" }
        payment_response = client.order.create(data=data)
        
        order_id = payment_response['id']
        order_status =payment_response['status']
        if order_status == 'created':
            payment = Payment(user = user, 
                              amount =totalamount, 
                              razorpay_order_id = order_id,
                              razorpay_payment_status = order_status)
            payment.save()
        
        context = {
            'cartitem': cartitem,
            'add': add,
            'cart_items': cart_items,
            'famount': famount,
            'totalamount': totalamount,
            'shipping_fee': shipping_fee,
            'razoramount': razoramount,
            'order_id': order_id,
            'RAZOR_KEY_ID': settings.RAZOR_KEY_ID,
        }
        return render(request, "checkout.html", context)
    
@login_required    
def paymentdone(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')
    # print(f'payment done oid ={order_id, }, pid ={payment_id}, cid = {cust_id}')
    user = request.user
    if not cust_id:
        messages.error(request, "Delivery information missing. Please contact support.")
        return redirect('orders')
    customer = Customer.objects.get(id=cust_id)
    
    if customer.city.lower() != 'ahmedabad':
        messages.error(request, "We currently only accept orders from Ahmedabad. Coming soon to other cities!")
        return redirect('showcart')

    # To update payment status and payment id 
    payment =Payment.objects.get(razorpay_order_id=order_id)
    payment.paid =True
    payment.razorpay_order_id= order_id
    payment.razorpay_payment_id= payment_id

    payment.save()

    # to save order details
    cart = Cart.objects.filter(user=user)
    size_map = {'500gm': 0.5, '500g': 0.5, '1kg': 1, '2kg': 2, '500ml': 0.5, '1l': 1, '1lt': 1, '2l': 2, '2lt': 2}
    product_deductions = {}
    
    # First, create OrderPlaced records and aggregate stock deductions
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity,size=c.size,price=c.price,payment=payment,cust_id = customer.id).save()
        
        # Calculate size multiplier
        size_str = str(c.size).lower().replace(' ', '')
        size_val = 1
        for key, val in size_map.items():
            if key in size_str:
                size_val = val
                break
        total_decrement = c.quantity * size_val
        
        # Aggregate deductions by product ID
        if c.product.id not in product_deductions:
            product_deductions[c.product.id] = {'product': c.product, 'deduct': 0}
        product_deductions[c.product.id]['deduct'] += total_decrement
        c.delete()
    
    # Now deduct stock for each product only once
    for prod_info in product_deductions.values():
        product = prod_info['product']
        total_decrement = prod_info['deduct']
        if product.quantity >= total_decrement:
            product.quantity -= total_decrement
        else:
            product.quantity = 0
        product.save()
    
    return redirect('orders')

@login_required
def checkout_cod(request):
    if request.method == 'POST':
        user = request.user
        cust_id = request.POST.get('custid')
        if not cust_id:
            messages.error(request, "Please select a delivery address.")
            return redirect('checkout')
        
        try:
            customer = Customer.objects.get(id=cust_id, user=user)
            if customer.city.lower() != 'ahmedabad':
                messages.warning(request, "Currently, we only deliver to Ahmedabad. We're coming soon to your city!")
                return redirect('checkout')
        except Customer.DoesNotExist:
            messages.error(request, "Invalid address selected.")
            return redirect('checkout')
            
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('showcart')
            
        # Validate that cart items don't exceed available stock
        for item in cart_items:
            if item.quantity > item.product.quantity:
                messages.error(request, f"Sorry, the requested quantity for {item.product.title} exceeds our available stock ({item.product.quantity} left). Please update your cart.")
                return redirect('showcart')
            
        famount = 0
        for p in cart_items:
            # We use the price stored in the cart item which already accounts for size multipliers
            famount += p.quantity * p.price
            
        shipping_fee = 0 if famount >= 500 else (40 if famount > 0 else 0)
        totalamount = famount + shipping_fee
        
        # Create payment record for COD
        payment = Payment(
            user=user,
            amount=totalamount,
            razorpay_payment_status='Cash On Delivery',
            paid=False
        )
        payment.save()
        
        # Save order details
        size_map = {'500gm': 0.5, '500g': 0.5, '1kg': 1, '2kg': 2, '500ml': 0.5, '1l': 1, '1lt': 1, '2l': 2, '2lt': 2}
        product_deductions = {}
        
        # First, create OrderPlaced records and aggregate stock deductions
        for c in cart_items:
            OrderPlaced(
                user=user,
                customer=customer,
                product=c.product,
                quantity=c.quantity,
                size=c.size,
                price=c.price,
                payment=payment,
                cust_id=customer.id
            ).save()
            
            # Calculate size multiplier
            size_str = str(c.size).lower().replace(' ', '')
            size_val = 1
            for key, val in size_map.items():
                if key in size_str:
                    size_val = val
                    break
            total_decrement = c.quantity * size_val
            
            # Aggregate deductions by product ID
            if c.product.id not in product_deductions:
                product_deductions[c.product.id] = {'product': c.product, 'deduct': 0}
            product_deductions[c.product.id]['deduct'] += total_decrement
            c.delete()
        
        # Now deduct stock for each product only once
        for prod_info in product_deductions.values():
            product = prod_info['product']
            total_decrement = prod_info['deduct']
            if product.quantity >= total_decrement:
                product.quantity -= total_decrement
            else:
                product.quantity = 0
            product.save()
            
        messages.success(request, "Order placed successfully! Please keep cash ready for delivery.")
        return redirect('orders')
    
    return redirect('checkout')


@login_required
def orders(request):
    cartitem = cart_num(request)
    query = request.GET.get('q')
    queryset = OrderPlaced.objects.filter(user=request.user).select_related('product', 'payment', 'customer').order_by('-ordered_date')
    
    if query:
        queryset = queryset.filter(
            Q(payment__razorpay_order_id__icontains=query) |
            Q(product__title__icontains=query) |
            Q(status__icontains=query) |
            Q(payment__id__icontains=query.replace('COD', '').replace('cod', ''))
        ).distinct()
        
    order_groups = get_grouped_orders(queryset)
    return render(request, "orders.html", locals())

def search(request):
    query = request.GET.get('search', '')
    product = Product.objects.filter(Q(title__icontains=query)).exclude(product_image='').order_by('-id')
    cartitem = cart_num(request)
    return render(request, "search.html",locals())

from django.contrib.auth.decorators import user_passes_test

from collections import OrderedDict

def get_grouped_orders(queryset):
    grouped_orders = OrderedDict()
    for item in queryset:
        key = f"P{item.payment.id}" if item.payment else f"I{item.id}"
        if key not in grouped_orders:
            if item.payment:
                if item.payment.razorpay_order_id:
                    order_id_display = f"{item.payment.razorpay_order_id[-8:].upper()}"
                else:
                    order_id_display = f"COD{item.payment.id:05d}"
            else:
                order_id_display = f"ORD{item.id:05d}"
                
            grouped_orders[key] = {
                'id': order_id_display,
                'payment': item.payment,
                'items': [],
                'status': item.status,
                'ordered_date': item.ordered_date,
                'customer': item.customer,
                'total_amount': 0,
                'earning': 0,
                'delivery_person': item.delivery_person,
                'first_item_id': item.id,
                'user': item.user
            }
        grouped_orders[key]['items'].append(item)
        grouped_orders[key]['total_amount'] += item.total_cost
    
    # Finalize calculations for each group
    for group in grouped_orders.values():
        total = group['total_amount']
        # Calculation: 30 base + 5% of total
        group['earning'] = round(30 + (total * 0.05), 2)
        
    return list(grouped_orders.values())

def is_admin(user):
    return user.is_superuser or user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_products = Product.objects.count()
    
    # Group all orders to count unique transactions
    all_orders_queryset = OrderPlaced.objects.all().select_related('payment')
    all_grouped = get_grouped_orders(all_orders_queryset)
    total_orders = len(all_grouped)
    
    total_customers = User.objects.filter(is_superuser=False).count()
    
    # Calculate total revenue from paid payments
    from django.db.models import Sum
    total_revenue = Payment.objects.filter(paid=True).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Pending orders (unique groups)
    pending_orders = len([g for g in all_grouped if g['status'] == 'Pending'])
    
    # Latest 5 grouped orders
    latest_orders_qs = OrderPlaced.objects.all().select_related('product', 'payment', 'customer').order_id_display = None # Dummy for locals
    latest_orders = get_grouped_orders(OrderPlaced.objects.all().order_by('-ordered_date'))[:5]
    
    return render(request, 'admin_panel/dashboard.html', locals())

@user_passes_test(is_admin)
def admin_products(request):
    query = request.GET.get('q')
    products = Product.objects.all().order_by('-id')
    if query:
        # Match against human-readable category names
        matching_cat_codes = [code for code, name in CATEGORY_CHOICES if query.lower() in name.lower()]
        
        products = products.filter(
            Q(title__icontains=query) |
            Q(category__in=matching_cat_codes)
        ).distinct()
    return render(request, 'admin_panel/products.html', locals())

@user_passes_test(is_admin)
def admin_add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('admin-products')
    else:
        form = ProductForm()
    return render(request, 'admin_panel/add_product.html', locals())

@user_passes_test(is_admin)
def admin_update_product(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('admin-products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin_panel/add_product.html', locals())

@user_passes_test(is_admin)
def admin_delete_product(request, pk):
    product = Product.objects.get(pk=pk)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('admin-products')

@user_passes_test(is_admin)
def admin_orders(request):
    query = request.GET.get('q')
    queryset = OrderPlaced.objects.all().select_related('product', 'payment', 'customer', 'delivery_person').order_by('-ordered_date')
    
    if query:
        queryset = queryset.filter(
            Q(payment__razorpay_order_id__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(customer__mobile__icontains=query) |
            Q(status__icontains=query) |
            Q(payment__id__icontains=query.replace('COD', '').replace('cod', ''))
        ).distinct()
        
    order_groups = get_grouped_orders(queryset)
    return render(request, 'admin_panel/orders.html', locals())

def restore_stock(order):
    product = order.product
    product.quantity += order.quantity
    product.save()

def send_cancellation_email(order):
    user_email = order.user.email
    if not user_email:
        return
        
    subject = f"Order Cancelled - #ORD-{order.id}"
    
    if order.payment.razorpay_payment_status == 'Cash On Delivery':
        message = f"Hi {order.user.username},\n\nSorry, your product (Order #ORD-{order.id}) is cancelled. Sorry for the inconveniences."
    else:
        message = f"Hi {order.user.username},\n\nYour order (Order #ORD-{order.id}) is cancelled. Your payment will be refunded."
        
    from_email = settings.DEFAULT_FROM_EMAIL
    try:
        send_mail(subject, message, from_email, [user_email])
    except Exception as e:
        print(f"Error sending cancellation email: {e}")

@user_passes_test(is_admin)
def admin_update_order(request, pk):
    # This now updates the ENTIRE group of orders associated with the same payment
    order_instance = OrderPlaced.objects.get(pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        # Get all orders in this group
        if order_instance.payment:
            group_items = OrderPlaced.objects.filter(payment=order_instance.payment)
        else:
            group_items = OrderPlaced.objects.filter(id=pk)

        for order in group_items:
            old_status = order.status
            if new_status == 'Cancel' and old_status != 'Cancel':
                restore_stock(order)
                send_cancellation_email(order)
            
            order.status = new_status
            order.save()
            
        messages.success(request, f"Order group status updated to {new_status}!")
        return redirect('admin-orders')
    return redirect('admin-orders')

@login_required
def cancel_order(request, pk):
    try:
        order_instance = OrderPlaced.objects.get(pk=pk, user=request.user)
    except OrderPlaced.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('orders')
        
    if order_instance.status in ['Pending', 'Accepted']:
        if order_instance.payment:
            group_items = OrderPlaced.objects.filter(payment=order_instance.payment, user=request.user)
        else:
            group_items = OrderPlaced.objects.filter(id=pk, user=request.user)

        for obj in group_items:
            obj.status = 'Cancel'
            obj.save()
            restore_stock(obj)
            send_cancellation_email(obj)
            
        messages.success(request, "Order group cancelled successfully. Stock has been restored and notification sent.")
    else:
        messages.error(request, "Order cannot be cancelled at this stage.")
        
    return redirect('orders')

@user_passes_test(is_admin)
def admin_customers(request):
    query = request.GET.get('q')
    customers = Customer.objects.all().order_by('-id')
    if query:
        customers = customers.filter(
            Q(name__icontains=query) |
            Q(mobile__icontains=query) |
            Q(locality__icontains=query) |
            Q(city__icontains=query) |
            Q(user__username__icontains=query)
        ).distinct()
    return render(request, 'admin_panel/customers.html', locals())

@user_passes_test(is_admin)
def admin_add_customer(request):
    if request.method == 'POST':
        form = AdminCustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer detail added successfully!")
            return redirect('admin-customers')
    else:
        form = AdminCustomerForm()
    return render(request, 'admin_panel/add_customer.html', locals())

@user_passes_test(is_admin)
def admin_update_customer(request, pk):
    customer = Customer.objects.get(pk=pk)
    if request.method == 'POST':
        form = AdminCustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer detail updated successfully!")
            return redirect('admin-customers')
    else:
        form = AdminCustomerForm(instance=customer)
    return render(request, 'admin_panel/add_customer.html', locals())

@user_passes_test(is_admin)
def admin_delete_customer(request, pk):
    customer = Customer.objects.get(pk=pk)
    customer.delete()
    messages.success(request, "Customer detail deleted successfully!")
    return redirect('admin-customers')

@user_passes_test(is_admin)
def admin_payments(request):
    query = request.GET.get('q')
    payments = Payment.objects.all().order_by('-id')
    if query:
        payments = payments.filter(
            Q(razorpay_order_id__icontains=query) |
            Q(razorpay_payment_id__icontains=query) |
            Q(razorpay_payment_status__icontains=query) |
            Q(user__username__icontains=query)
        ).distinct()
    return render(request, 'admin_panel/payments.html', locals())

@login_required
def submit_review(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        
        # PRODUCER VALIDATION: Only allow review if they bought and received it
        has_bought = OrderPlaced.objects.filter(user=request.user, product=product, status='Delivered').exists()
        if not has_bought:
            messages.error(request, "You can only review products you have historically received.")
            return redirect('product-detail', pk=product_id)

        # Check if user already reviewed this product
        existing_review = ProductReview.objects.filter(user=request.user, product=product).first()
        
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            if existing_review:
                existing_review.rating = form.cleaned_data['rating']
                existing_review.comment = form.cleaned_data['comment']
                existing_review.save()
                messages.success(request, "Review updated successfully!")
            else:
                review = form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()
                messages.success(request, "Thank you for your review!")
        else:
            messages.error(request, "Invalid input in review form.")
            
    return redirect('product-detail', pk=product_id)

@user_passes_test(is_admin)
def admin_reviews(request):
    query = request.GET.get('q')
    reviews = ProductReview.objects.all().select_related('user', 'product').order_by('-created_at')
    if query:
        reviews = reviews.filter(
            Q(user__username__icontains=query) |
            Q(product__title__icontains=query) |
            Q(comment__icontains=query) |
            Q(rating__icontains=query)
        ).distinct()
    return render(request, 'admin_panel/reviews.html', locals())

@user_passes_test(is_admin)
def admin_delete_review(request, pk):
    review = ProductReview.objects.get(pk=pk)
    review.delete()
    messages.success(request, "Review deleted successfully!")
    return redirect('admin-reviews')


import random
from django.core.mail import send_mail

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            otp = random.randint(100000, 999999)
            print(f"DEBUG: OTP for {email} is {otp}")
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            
            # Send Email
            subject = 'Password Reset OTP'
            message = f'Your OTP for password reset is {otp}'
            from_email = settings.DEFAULT_FROM_EMAIL
            try:
                send_mail(subject, message, from_email, [email])
                messages.success(request, 'OTP sent to your email.')
                return redirect('verify_otp')
            except Exception as e:
                print(f"Error sending email: {e}")
                messages.error(request, f"Failed to send email: {e}")
                return redirect('forgot_password')
        else:
            messages.error(request, 'No user associated with this email.')
            return redirect('forgot_password')
    return render(request, 'forgot_password.html')

def verify_otp_view(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        session_otp = request.session.get('reset_otp')
        if session_otp and str(otp) == str(session_otp):
            request.session['otp_verified'] = True
            messages.success(request, 'OTP verified successfully.')
            return redirect('reset_new_password')
        else:
            messages.error(request, 'Invalid OTP.')
            return redirect('verify_otp')
    return render(request, 'verify_otp.html')

def reset_new_password_view(request):
    email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified')
    
    if not email or not otp_verified:
        messages.error(request, "Please verify your email first.")
        return redirect('forgot_password')
        
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            user = User.objects.filter(email=email).first()
            if user:
                user.set_password(new_password)
                user.save()
                
                # Clear session
                for key in ['reset_otp', 'reset_email', 'otp_verified']:
                    if key in request.session:
                        del request.session[key]
                    
                messages.success(request, 'Password reset successfully. You can now login.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_new_password')
            
    return render(request, 'reset_new_password.html')

@login_required
def submit_complaint(request, order_id):
    order = OrderPlaced.objects.get(id=order_id, user=request.user)
    cartitem = cart_num(request)
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        Complaint.objects.create(user=request.user, order=order, subject=subject, message=message)
        messages.success(request, "Complaint submitted successfully. We will get back to you soon.")
        return redirect('orders')
    return render(request, 'submit_complaint.html', locals())

@login_required
def view_complaints(request):
    cartitem = cart_num(request)
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'view_complaints.html', locals())

@user_passes_test(is_admin)
def admin_complaints(request):
    query = request.GET.get('q')
    complaints = Complaint.objects.all().select_related('user', 'order').order_by('-created_at')
    if query:
        complaints = complaints.filter(
            Q(user__username__icontains=query) |
            Q(subject__icontains=query) |
            Q(message__icontains=query) |
            Q(status__icontains=query) |
            Q(order__id__icontains=query)
        ).distinct()
    return render(request, 'admin_panel/complaints.html', locals())

@user_passes_test(is_admin)
def admin_reply_complaint(request, pk):
    complaint = Complaint.objects.get(pk=pk)
    if request.method == 'POST':
        reply = request.POST.get('reply')
        complaint.reply = reply
        complaint.status = 'Resolved'
        complaint.save()
        messages.success(request, "Reply sent successfully!")
        return redirect('admin-complaints')
    return render(request, 'admin_panel/reply_complaint.html', locals())

# Delivery Person Functionality

def is_delivery_person(user):
    return hasattr(user, 'deliveryperson')

@login_required
@user_passes_test(is_delivery_person)
def delivery_dashboard(request):
    dp = request.user.deliveryperson
    assigned_orders_queryset = OrderPlaced.objects.filter(delivery_person=dp).select_related('payment')
    assigned_groups = get_grouped_orders(assigned_orders_queryset)
    
    total_assigned = len(assigned_groups)
    pending_deliveries = len([g for g in assigned_groups if g['status'] in ['Assigned', 'Out for Delivery']])
    completed_deliveries = len([g for g in assigned_groups if g['status'] == 'Delivered'])
    failed_deliveries = len([g for g in assigned_groups if g['status'] == 'Failed Delivery'])
    
    # Personal Earnings breakdown
    completed_delivery_groups = [g for g in assigned_groups if g['status'] == 'Delivered']
    COMMISSION_PER_DELIVERY = 50
    
    # Time-based breakdown
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    today_delivery_groups = [g for g in completed_delivery_groups if g['ordered_date'] >= today_start]
    month_delivery_groups = [g for g in completed_delivery_groups if g['ordered_date'] >= month_start]
    
    today_earnings = sum(g['earning'] for g in today_delivery_groups)
    month_earnings = sum(g['earning'] for g in month_delivery_groups)
    total_earnings = sum(g['earning'] for g in completed_delivery_groups)
    
    # COD Collection breakdown
    cod_delivery_groups = [g for g in completed_delivery_groups if g['payment'] and g['payment'].razorpay_payment_status == 'Cash On Delivery']
    total_cod_collected = sum(g['total_amount'] for g in cod_delivery_groups)
    
    return render(request, 'delivery/dashboard.html', locals())

@login_required
@user_passes_test(is_delivery_person)
def delivery_orders(request):
    dp = request.user.deliveryperson
    query = request.GET.get('q')
    queryset = OrderPlaced.objects.filter(delivery_person=dp).select_related('product', 'payment', 'customer').order_by('-ordered_date')
    
    if query:
        queryset = queryset.filter(
            Q(payment__razorpay_order_id__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(customer__mobile__icontains=query) |
            Q(status__icontains=query) |
            Q(payment__id__icontains=query.replace('COD', '').replace('cod', ''))
        ).distinct()
        
    order_groups = get_grouped_orders(queryset)
    return render(request, 'delivery/orders.html', locals())

@login_required
@user_passes_test(is_delivery_person)
def delivery_order_detail(request, pk):
    dp = request.user.deliveryperson
    order = OrderPlaced.objects.get(pk=pk, delivery_person=dp)
    
    # Get all items in this group
    if order.payment:
        group_items = OrderPlaced.objects.filter(payment=order.payment, delivery_person=dp)
        total_group_amount = sum(item.total_cost for item in group_items)
        if order.payment.razorpay_order_id:
            order_id_display = order.payment.razorpay_order_id[-8:].upper()
        else:
            order_id_display = f"COD{order.payment.id:05d}"
    else:
        group_items = [order]
        total_group_amount = order.total_cost
        order_id_display = f"ORD{order.id:05d}"
    # Calculate Dynamic Earning: 30 + 5% of total
    group_earning = round(30 + (total_group_amount * 0.05), 2)
        
    form = DeliveryStatusForm(instance=order)
    return render(request, 'delivery/order_detail.html', locals())

@login_required
@user_passes_test(is_delivery_person)
def delivery_update_status(request, pk):
    dp = request.user.deliveryperson
    order_instance = OrderPlaced.objects.get(pk=pk, delivery_person=dp)
    if request.method == 'POST':
        # Prevent updating if order is already Delivered or Failed Delivery
        if order_instance.status in ['Delivered', 'Failed Delivery']:
            return JsonResponse({'status': 'error', 'message': 'This order cannot be modified'}, status=400)
        
        new_status = request.POST.get('status')
        payment_collected = request.POST.get('payment_collected') == 'on'
        delivery_notes = request.POST.get('delivery_notes', '')

        if not new_status:
            return JsonResponse({'status': 'error', 'message': 'Status is required'}, status=400)

        # Update entire group
        if order_instance.payment:
            group_items = OrderPlaced.objects.filter(payment=order_instance.payment, delivery_person=dp)
        else:
            group_items = OrderPlaced.objects.filter(id=pk, delivery_person=dp)

        # If status is set to 'Out for Delivery', generate/send OTP
        if new_status == 'Out for Delivery':
            import random
            for order in group_items:
                otp = random.randint(100000, 999999)
                order.delivery_otp = str(otp)
                order.status = new_status
                if delivery_notes:
                    order.delivery_notes = delivery_notes
                order.save()
                # Send OTP to customer email
                customer_email = order.customer.user.email
                if customer_email:
                    subject = 'Your Delivery OTP - MILK&MORE'
                    message = f'Your OTP for order delivery confirmation is: {otp}\nPlease provide this OTP to the delivery person.'
                    from_email = settings.DEFAULT_FROM_EMAIL
                    try:
                        send_mail(subject, message, from_email, [customer_email])
                    except Exception as e:
                        print(f"Error sending OTP email: {e}")
            
            if payment_collected:
                for order in group_items:
                    if order.payment:
                        order.payment.paid = True
                        order.payment.save()
            
            return JsonResponse({'status': 'success', 'message': 'OTP sent to customer email'})

        # If status is set to 'Delivered', save payment status (OTP already verified by delivery_otp_verify)
        if new_status == 'Delivered':
            for order in group_items:
                if payment_collected and order.payment:
                    order.payment.paid = True
                    order.payment.save()
            
            return JsonResponse({'status': 'success', 'message': 'Order marked as delivered with payment recorded'})

        # If status is set to 'Failed Delivery', send refund notification email
        if new_status == 'Failed Delivery':
            for order in group_items:
                order.status = new_status
                if delivery_notes:
                    order.delivery_notes = delivery_notes
                order.save()
                
                # Send refund notification email to customer
                customer_email = order.customer.user.email
                if customer_email:
                    subject = "Order Failed - Refund Notification - MILK&MORE"
                    if order.payment and order.payment.razorpay_payment_status != 'Cash On Delivery':
                        message = (
                            f"Hi {order.customer.name},\n\n"
                            f"Unfortunately, we couldn't deliver your order (#{order.id}) successfully. We sincerely apologize for the inconvenience.\n\n"
                            f"Your payment has been processed online. We will refund your money back to your original payment method within 5-7 business days.\n\n"
                            f"If you have any questions, please contact us at 9327558924 or reply to this email.\n\n"
                            f"Thank you for your understanding.\n\n"
                            f"Best regards,\nMILK&MORE Team"
                        )
                    else:
                        message = (
                            f"Hi {order.customer.name},\n\n"
                            f"Unfortunately, we couldn't deliver your order (#{order.id}) successfully. We sincerely apologize for the inconvenience.\n\n"
                            f"If you have any questions, please contact us at 9327558924 or reply to this email.\n\n"
                            f"Thank you for your understanding.\n\n"
                            f"Best regards,\nMILK&MORE Team"
                        )
                    from_email = settings.DEFAULT_FROM_EMAIL
                    try:
                        send_mail(subject, message, from_email, [customer_email])
                    except Exception as e:
                        print(f"Error sending failed delivery email: {e}")
            
            return JsonResponse({'status': 'success', 'message': 'Order marked as Failed Delivery. Customer notified.'})

        # For other statuses, update as usual
        for order in group_items:
            order.status = new_status
            if delivery_notes:
                order.delivery_notes = delivery_notes
            order.save()
            if payment_collected:
                if order.payment:
                    order.payment.paid = True
                    order.payment.save()
        
        return JsonResponse({'status': 'success', 'message': f'Order status updated to {new_status}'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
@user_passes_test(is_delivery_person)
def delivery_profile(request):
    dp = request.user.deliveryperson
    if request.method == 'POST':
        form = DeliveryPersonProfileForm(request.POST, instance=dp)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('delivery-profile')
    else:
        form = DeliveryPersonProfileForm(instance=dp)
    return render(request, 'delivery/profile.html', locals())

# OTP verification for delivery
@login_required
@user_passes_test(is_delivery_person)
def delivery_otp_verify(request, pk):
    dp = request.user.deliveryperson
    order = OrderPlaced.objects.get(pk=pk, delivery_person=dp)
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        if order.delivery_otp and otp_input and otp_input == order.delivery_otp:
            # Mark as delivered
            order.status = 'Delivered'
            order.delivery_otp = None
            order.save()
            # Send thank you/review email
            customer_email = order.customer.user.email
            if customer_email:
                subject = "Order Delivered - MILK&MORE"
                message = (
                    "Your order has been successfully delivered! Thank you for choosing MILK&MORE.\n\n"
                    "Please rate and review your product. If you faced any inconvenience, contact us at 9327558924 or add a complaint from your orders page."
                )
                from_email = settings.DEFAULT_FROM_EMAIL
                try:
                    send_mail(subject, message, from_email, [customer_email])
                except Exception as e:
                    print(f"Error sending delivery confirmation email: {e}")
            
            # Return JSON response for AJAX
            return JsonResponse({'status': 'success', 'message': 'OTP verified successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

# Admin side Delivery Person Management

@user_passes_test(is_admin)
def admin_delivery_persons(request):
    delivery_persons = DeliveryPerson.objects.all()
    
    # Enrich delivery persons with financial data
    for dp in delivery_persons:
        assigned_orders = OrderPlaced.objects.filter(delivery_person=dp).select_related('payment', 'product', 'customer').order_by('-ordered_date')
        grouped_orders = get_grouped_orders(assigned_orders)
        
        # Calculate totals only for Delivered groups
        dp.delivered_groups = [g for g in grouped_orders if g['status'] == 'Delivered']
        dp.total_earning = sum(g['earning'] for g in dp.delivered_groups)
        dp.total_collection = sum(g['total_amount'] for g in dp.delivered_groups if g['payment'] and g['payment'].razorpay_payment_status == 'Cash On Delivery')
        dp.completed_tasks = len(dp.delivered_groups)
        
    return render(request, 'admin_panel/delivery_persons.html', locals())

@user_passes_test(is_admin)
def admin_delivery_person_orders(request, pk):
    dp = DeliveryPerson.objects.get(pk=pk)
    # Get all delivered orders for this person
    assigned_orders = OrderPlaced.objects.filter(delivery_person=dp, status='Delivered').select_related('product', 'payment', 'customer').order_by('-ordered_date')
    order_groups = get_grouped_orders(assigned_orders)
    
    # Calculate totals for this specific view summary
    total_earnings = sum(g['earning'] for g in order_groups)
    total_collection = sum(g['total_amount'] for g in order_groups if g['payment'] and g['payment'].razorpay_payment_status == 'Cash On Delivery')
    
    return render(request, 'admin_panel/delivery_person_orders.html', locals())

@user_passes_test(is_admin)
def admin_add_delivery_person(request):
    if request.method == 'POST':
        form = DeliveryPersonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Delivery Person added successfully!")
            return redirect('admin-delivery-persons')
    else:
        form = DeliveryPersonForm()
    return render(request, 'admin_panel/add_delivery_person.html', locals())

@user_passes_test(is_admin)
def admin_update_delivery_person(request, pk):
    dp = DeliveryPerson.objects.get(pk=pk)
    if request.method == 'POST':
        form = DeliveryPersonForm(request.POST, instance=dp)
        if form.is_valid():
            form.save()
            messages.success(request, "Delivery Person updated successfully!")
            return redirect('admin-delivery-persons')
    else:
        form = DeliveryPersonForm(instance=dp)
    return render(request, 'admin_panel/add_delivery_person.html', locals())

@user_passes_test(is_admin)
def admin_delete_delivery_person(request, pk):
    dp = DeliveryPerson.objects.get(pk=pk)
    dp.delete()
    messages.success(request, "Delivery Person deleted successfully!")
    return redirect('admin-delivery-persons')

@user_passes_test(is_admin)
def admin_assign_order(request, pk):
    order_instance = OrderPlaced.objects.get(pk=pk)
    delivery_persons = DeliveryPerson.objects.filter(is_active=True)
    
    if order_instance.payment:
        group_items = OrderPlaced.objects.filter(payment=order_instance.payment)
    else:
        group_items = OrderPlaced.objects.filter(id=pk)
        
    if request.method == 'POST':
        dp_id = request.POST.get('delivery_person')
        if dp_id:
            dp = DeliveryPerson.objects.get(id=dp_id)
            for order in group_items:
                order.delivery_person = dp
                order.status = 'Assigned'
                order.save()
            messages.success(request, f"Order group assigned to {dp.name} successfully!")
            return redirect('admin-orders')
    return render(request, 'admin_panel/assign_order.html', locals())

@login_required
def download_invoice(request, payment_id):
    try:
        # If user is admin, they can download any invoice. Otherwise, only their own.
        if is_admin(request.user):
            payment = Payment.objects.get(id=payment_id)
            orders = OrderPlaced.objects.filter(payment=payment)
        else:
            payment = Payment.objects.get(id=payment_id, user=request.user)
            orders = OrderPlaced.objects.filter(payment=payment, user=request.user)
    except Payment.DoesNotExist:
        messages.error(request, "Invoice not found or unauthorized.")
        return redirect('orders')
        
    if not orders.exists():
        messages.error(request, "No orders found for this invoice.")
        return redirect('orders')
        
    # Get the customer details from the first order (they should all be the same for one payment)
    customer = orders.first().customer
    
    context = {
        'payment': payment,
        'orders': orders,
        'customer': customer,
    }
    
    # Render HTML template to a string
    template = get_template('invoice_template.html')
    html = template.render(context)
    
    # Create a PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{payment.id}.pdf"'
        return response
    
    messages.error(request, "Error generating PDF invoice.")
    return redirect('orders')