from .models import Wishlist, Cart

def wishlist_count(request):
    count = 0
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        count = wishlist.products.count()
    return {'wishlist_count': count}

def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        count = cart.items.count()
    return {'cart_count': count}
