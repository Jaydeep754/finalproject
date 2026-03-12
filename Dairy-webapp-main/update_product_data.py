import os
import django
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ec.settings')
django.setup()

from app.models import Product

def update_products():
    now = datetime.now().date()
    
    expiry_map = {
        'MK': 3,   # Milk
        'LS': 7,   # Lassi
        'BS': 10,  # Basundi
        'MT': 10,  # Matho
        'SW': 30,  # Sweets
        'IC': 90,  # Icecream
    }
    
    products = Product.objects.all()
    count = 0
    
    for product in products:
        # Set expiry date based on category
        days = expiry_map.get(product.category, 7)
        product.expiry_date = now + timedelta(days=days)
        
        # Set random-ish stock quantity if not already set or just reset them
        import random
        product.quantity = random.randint(50, 200)
        
        product.save()
        count += 1
        print(f"Updated {product.title}: Quantity={product.quantity}, Expiry={product.expiry_date}")

    print(f"Successfully updated {count} products.")

if __name__ == "__main__":
    update_products()
