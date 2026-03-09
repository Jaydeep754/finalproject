import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ec.settings')
django.setup()

from app.models import Product

def update_prices_to_1kg():
    products = Product.objects.all()
    count = 0
    for product in products:
        # Assuming old prices were based on 500gm = 1x, now 1kg = 1x
        # To maintain the same value per weight, we double the stored price
        # as it now represents 1kg instead of 500gm.
        product.selling_price *= 2
        product.discounted_price *= 2
        product.save()
        count += 1
        print(f"Updated {product.title}: New 1kg Price = ₹{product.discounted_price}")

    print(f"\nSuccessfully updated {count} products to 1kg/1L baseline.")

if __name__ == "__main__":
    update_prices_to_1kg()
