from django.contrib import admin
from django.contrib.auth.models import User
from .models import Category, Product, UserProductInteraction, Review, Wishlist


# Register Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

# Register Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'image')
    list_filter = ('category',)
    search_fields = ('name', 'description')

    # If you want only admins to update images but allow staff to edit other fields
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:  # Only allow superuser to edit image
            return ('image',)
        return ()

# Register User Product Interaction
@admin.register(UserProductInteraction)
class UserProductInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'interaction_type', 'timestamp')
    list_filter = ('interaction_type', 'timestamp')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user',)
