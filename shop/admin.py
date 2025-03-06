from django.contrib import admin
from .models import Category, Product, Review, Cart, CartItem, Order, NewsletterSignup, Wishlist
from django.contrib.auth.models import User

class CartItemAdmin(admin.ModelAdmin):
    readonly_fields = [field.name for field in CartItem._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class CartAdmin(admin.ModelAdmin):

    readonly_fields = [field.name for field in Cart._meta.fields] + ['total_price_display']

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj = None):
        return False
    
    def has_delete_permission(self, request, obj = None):
        return False
    
    def total_price_display(self, obj):
        return obj.total_price()


class OrderAdmin(admin.ModelAdmin):

    readonly_fields = [field.name for field in Order._meta.fields if field.name not in ('order_status', 'tracking_number')]

    def has_add_permission(self, request):
        return True  
    
    def has_change_permission(self, request, obj=None):
        return True  

    def has_delete_permission(self, request, obj=None):
        return False
    
class NewsletterSignupAdmin(admin.ModelAdmin):

    readonly_fields = [field.name for field in NewsletterSignup._meta.fields]

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj = None):
        return False
    
    def has_delete_permission(self, request, obj = None):
        return False
    
class ReviewAdmin(admin.ModelAdmin):

    readonly_fields = [field.name for field in Review._meta.fields]

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj = None):
        return False
    
    def has_delete_permission(self, request, obj = None):
        return False
    
class WishlistAdmin(admin.ModelAdmin):

    readonly_fields = [field.name for field in Wishlist._meta.fields]

    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj = None):
        return False
    
    def has_delete_permission(self, request, obj = None):
        return False
    
class CustomUser(admin.ModelAdmin):
      
    readonly_fields = [field.name for field in User._meta.fields if field.name not in ('is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions')]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True  

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(NewsletterSignup,NewsletterSignupAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUser)