from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Review, UserProductInteraction, Wishlist
from .serializers import ProductSerializer
from .recommender import get_user_recommendations
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .forms import ProductForm, ReviewForm  # We'll create this in step 3
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required



def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Creates the new user
            return redirect('login')  # Redirect to the login page after signup
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})
# Frontend Views

def home(request):
    products = Product.objects.all()
    recommendations = None
    if request.user.is_authenticated:
        recommendations = get_user_recommendations(request.user.id)
    context = {
        'products': products,
        'recommendations': recommendations,
    }
    return render(request, 'store/index.html', context)




def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'store/profile.html')


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

# Wishlist section

def get_user_wishlist(user):
    # Returns the wishlist for a user, creating it if necessary
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    return wishlist

# from django.contrib.auth.decorators import login_required

@login_required
def wishlist_view(request):
    wishlist = get_user_wishlist(request.user)
    context = {
        'wishlist_products': wishlist.products.all()
    }
    return render(request, 'store/wishlist.html', context)

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_user_wishlist(request.user)
    wishlist.products.add(product)
    return redirect('store:wishlist')

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_user_wishlist(request.user)
    wishlist.products.remove(product)
    return redirect('store:wishlist')





def cart(request):
    # Retrieve the cart from session; the cart is stored as a dict: {product_id: quantity}
    cart = request.session.get('cart', {})
    cart_items = []
    grand_total = 0
    for pid, quantity in cart.items():
        product = get_object_or_404(Product, pk=pid)
        total = product.price * quantity
        grand_total += total
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total': total,
        })
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'grand_total': grand_total})

def add_to_cart(request, product_id):
    # Get the product (404 if not found)
    product = get_object_or_404(Product, pk=product_id)
    cart = request.session.get('cart', {})
    # Increase the quantity or add the product
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart  # Save back to session
    return redirect('store:cart')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    # Remove the product if it exists in the cart
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('store:cart')

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def update_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        action = data.get('action')
        
        # Retrieve the cart from session
        cart = request.session.get('cart', {})
        # Get the product details (price etc.) from the database
        from .models import Product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found.'})
        
        # Process the action
        if action == 'increment':
            cart[product_id] = cart.get(product_id, 0) + 1
        elif action == 'decrement':
            # Decrement only if quantity is greater than 1; if it becomes 0, remove it
            if cart.get(product_id, 0) > 1:
                cart[product_id] = cart.get(product_id, 0) - 1
            else:
                cart.pop(product_id, None)
                action = 'remove'  # Indicate removal
        elif action == 'remove':
            cart.pop(product_id, None)
        
        request.session['cart'] = cart  # Save the cart back into the session
        
        # Recalculate totals
        new_quantity = cart.get(product_id, 0)
        new_total = new_quantity * product.price if new_quantity else 0
        
        # Calculate grand total
        grand_total = 0
        for pid, qty in cart.items():
            try:
                prod = Product.objects.get(id=pid)
                grand_total += prod.price * qty
            except Product.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True,
            'new_quantity': new_quantity,
            'new_total': new_total,
            'grand_total': grand_total,
            'action': action
        })
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


from django.contrib.admin.views.decorators import staff_member_required
# from django.shortcuts import get_object_or_404

@staff_member_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('store:product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/edit_product.html', {'form': form, 'product': product})


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Check if the user already reviewed the product if needed
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('store:product_detail', product_id=product.id)
    else:
        form = ReviewForm()
    return render(request, 'store/add_review.html', {'form': form, 'product': product})

def checkout(request):
    # For now, simply render a checkout page
    return render(request, 'store/checkout.html')

# Authentication
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  # Creates a new user
            return redirect('login')  # Redirect to login after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})


# API Views

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'price']

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductRecommendationsView(APIView):
    def get(self, request, user_id):
        recommended_products = get_user_recommendations(user_id)
        serializer = ProductSerializer(recommended_products, many=True)
        return Response(serializer.data)

# Product Creation (for adding image to product)
# from django.shortcuts import render, redirect
# from .forms import ProductForm

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Notice request.FILES for image upload
        if form.is_valid():
            form.save()
            return redirect('store:products')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})

