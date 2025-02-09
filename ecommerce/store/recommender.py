# store/recommender.py
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from .models import UserProductInteraction, Product

def get_user_item_matrix():
    """
    Construct a user-item matrix where rows are users, columns are products,
    and cell values represent the count of interactions.
    """
    interactions = UserProductInteraction.objects.all().values('user_id', 'product_id')
    df = pd.DataFrame(list(interactions))
    if df.empty:
        return None
    # Create a pivot table: rows are user_ids, columns are product_ids
    user_item_matrix = df.groupby(['user_id', 'product_id']).size().unstack(fill_value=0)
    return user_item_matrix

def train_recommendation_model(user_item_matrix):
    """
    Train a NearestNeighbors model on the user-item matrix.
    """
    model = NearestNeighbors(metric='cosine', algorithm='brute')
    model.fit(user_item_matrix.values)
    return model

# store/recommender.py
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from .models import UserProductInteraction, Product

def get_user_item_matrix():
    """
    Construct a user-item matrix where rows are users, columns are products,
    and cell values represent the count of interactions.
    """
    interactions = UserProductInteraction.objects.all().values('user_id', 'product_id')
    df = pd.DataFrame(list(interactions))
    if df.empty:
        return None
    # Create a pivot table: rows are user_ids, columns are product_ids
    user_item_matrix = df.groupby(['user_id', 'product_id']).size().unstack(fill_value=0)
    return user_item_matrix

def train_recommendation_model(user_item_matrix):
    """
    Train a NearestNeighbors model on the user-item matrix.
    """
    model = NearestNeighbors(metric='cosine', algorithm='brute')
    model.fit(user_item_matrix.values)
    return model

def get_user_recommendations(user_id, n_recommendations=5):
    """
    Recommend products for a given user using a collaborative filtering approach.
    """
    user_item_matrix = get_user_item_matrix()
    if user_item_matrix is None or user_item_matrix.empty:
        return Product.objects.none()  # Return empty if no interactions exist

    # Ensure user_id is in the index
    if user_id not in user_item_matrix.index:
        return Product.objects.order_by('-id')[:n_recommendations]  # Fallback to latest products

    model = train_recommendation_model(user_item_matrix)
    
    try:
        user_index = list(user_item_matrix.index).index(user_id)
    except ValueError:
        return Product.objects.order_by('-id')[:n_recommendations]  # Fallback

    # Ensure `n_neighbors` does not exceed available users
    available_users = len(user_item_matrix)
    n_neighbors = min(n_recommendations + 1, available_users)

    # Get nearest neighbors
    distances, indices = model.kneighbors([user_item_matrix.iloc[user_index].values], n_neighbors=n_neighbors)
    similar_user_indices = indices.flatten()[1:]  # Exclude the first (current user)

    if not len(similar_user_indices):
        return Product.objects.order_by('-id')[:n_recommendations]  # Return popular products if no similar users

    similar_user_ids = user_item_matrix.index[similar_user_indices]

    # Get products interacted with by similar users but not by the given user
    user_product_ids = set(UserProductInteraction.objects.filter(user_id=user_id)
                                                   .values_list('product_id', flat=True))

    recommended_product_ids = set(UserProductInteraction.objects.filter(user_id__in=similar_user_ids)
                                                          .exclude(product_id__in=user_product_ids)
                                                          .values_list('product_id', flat=True))

    if not recommended_product_ids:
        return Product.objects.order_by('-id')[:n_recommendations]  # Return popular products as fallback

    recommended_products = Product.objects.filter(id__in=recommended_product_ids)[:n_recommendations]

    return recommended_products
