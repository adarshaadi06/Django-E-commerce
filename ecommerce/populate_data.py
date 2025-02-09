from django.contrib.auth.models import User
from store.models import Product, UserProductInteraction
import random

# Create sample users
for i in range(5):
    User.objects.create_user(username=f'user{i}', password='testpassword')

# Create sample products
products = []
for i in range(10):
    product = Product.objects.create(name=f'Product {i}', price=random.randint(10, 100))
    products.append(product)

# Generate sample interactions
users = User.objects.all()
for user in users:
    for product in random.sample(products, k=5):  # Each user interacts with 5 random products
        UserProductInteraction.objects.create(user=user, product=product, rating=random.randint(1, 5))

print("Sample data populated successfully!")
