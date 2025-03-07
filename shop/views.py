from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category, Product, Cart, CartItem, Order, Wishlist, NewsletterSignup
from .forms import RegistrationForm, LoginForm, ReviewForm, NewsletterSignupForm
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import stripe
from django.conf import settings


def home(request):
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {'categories': categories})

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'shop/category_products.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at') 
    review_form = ReviewForm()   

    if request.method == 'POST':
        if request.user.is_authenticated:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.user = request.user  
                review.product = product     
                review.save()
                messages.success(request, "Your review has been submitted!")
                return redirect('product_detail', product_id=product.id)
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            messages.error(request, "You must be logged in to leave a review.")
            return redirect('login')

    context = {
        'product' : product,
        'reviews' : reviews,
        'review_form' : review_form
    }
    return render(request, 'shop/product_detail.html', context)

@login_required
def user_profile(request):
    if request.method == 'POST': 
        request.user.first_name = request.POST.get('first_name') 
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()
        return render(request, 'shop/profile.html', {'success': 'Profile updated successfully.'})
    
    return render(request, 'shop/profile.html')

@login_required
def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user= request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'Added {product.name} to cart.')
    return redirect('cart')

@login_required
def cart(request):
    cart, created= Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total = cart.total_price() if cart_items else 0
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'cart_total': total
    })

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            messages.error(request, 'Quantity must be at least 1.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated.')
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1  
        cart_item.save()
        messages.success(request, 'One quantity removed from cart.')
    else:
        cart_item.delete()  
        messages.success(request, 'Item removed from cart.')

    return redirect('cart')

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        shipping_address = request.POST.get('address')
        payment_method = request.POST.get('payment')
        token = request.POST.get('stripeToken')

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            for item in cart.items.all():
                if item.product.stock < item.quantity:
                    messages.error(request, f'Sorry, "{item.product.name}" is out of stock.')
                    return redirect('checkout')
                
                for item in cart.items.all():
                    item.product.stock -= item.quantity
                    item.product.save()

            charge = stripe.Charge.create(
                amount=int(cart.total_price() * 100), 
                currency='inr', 
                description=f"Order for {request.user.email}",
                source=token  
            )

            order = Order.objects.create(
                user=request.user,
                cart=cart,
                shipping_address=shipping_address,
                payment_method=payment_method,
                order_status='processing'
            )

            cart.items.all().delete()

            messages.success(request, 'Order placed successfully!')
            return redirect('order_confirmation', order_id=order.id)

        except stripe.error.CardError as e:
            messages.error(request, f'Payment failed: {e}')
            return redirect('checkout')

    return render(request, 'shop/checkout.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])   
            user.save()

            send_mail(
                'Welcome',
                '''Welcome to our Website
                   Thank you for register.''',
                'pateldrashti0106@gmail.com',
                [form.cleaned_data['email']],  
                fail_silently=False,  
            )
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Logged in successfully.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials.')
    else:
        form = LoginForm()
    return render(request, 'shop/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')

def search(request):
    query = request.GET.get('query', '')
    results = Product.objects.filter(name__icontains=query)
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'shop/search_results.html', context)

def product_list(request):

    products = Product.objects.all()

    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    if category_id:
        products = products.filter(category__id = category_id)

    if min_price:
        products = products.filter(price__gte = min_price)

    if max_price:
        products = products.filter(price__lte = max_price)

    if sort:
        if sort == 'price_asc':
            products = products.order_by('price')
        elif sort == 'price_desc':
            products = products.order_by('-price') 

    categories = Category.objects.all()
 
    context = {
        'products' : products,
        'categories' : categories
    }

    return render(request, 'shop/product_list.html', context)

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_confirmation.html', {'order': order})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if product in wishlist.products.all():
        messages.info(request, f"{product.name} is already in your wishlist.")
    else:
        wishlist.products.add(product)
        messages.success(request, f"{product.name} has been added to your wishlist!")
    
    return redirect('product_detail', product_id=product.id)

#display
@login_required
def wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.all()
    context = {
        'products': products,
    }
    return render(request, 'shop/wishlist.html', context)

def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.objects.get(user=request.user)  

    if product in wishlist.products.all():
        wishlist.products.remove(product)  
        wishlist.save()

    return redirect('wishlist') 

@login_required  
def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsletterSignupForm(request.POST)
        if form.is_valid():
            form.save()
            
            send_mail(
                'Newsletter Signup Confirmation',
                'Thank you for signing up for our newsletter!',
                'pateldrashti0106@gmail.com',  
                [form.cleaned_data['email']],  
                fail_silently=False,
            )
       
            messages.success(request, 'Thank you for signing up for our newsletter!')
        
            return redirect('home')
    else:
        form = NewsletterSignupForm()

    return redirect('home')

