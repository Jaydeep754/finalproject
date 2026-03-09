import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ec.settings')
django.setup()

from app.models import Product

def add_penda_products():
    penda_products = [
        {
            'title': 'Chocolate Penda',
            'selling_price': 520,
            'discounted_price': 480,
            'description': 'A fusion of traditional dairy sweetness and rich cocoa flavor.',
            'composition': 'Milk Solids, Sugar, Cocoa Powder, Cardamom',
            'category': 'SW',
            'product_image': 'product/choclatependa.jpeg'
        },
        {
            'title': 'Classic Kesar Penda',
            'selling_price': 600,
            'discounted_price': 550,
            'description': 'Golden hued penda infused with premium saffron and garnished with pistachios.',
            'composition': 'Khoa, Sugar, Saffron, Pistachio',
            'category': 'SW',
            'product_image': 'product/kesarpenda.jpeg'
        },
        {
            'title': 'Traditional Malai Penda',
            'selling_price': 550,
            'discounted_price': 500,
            'description': 'Soft and creamy traditional malai penda that melts in your mouth.',
            'composition': 'Fresh Malai, Milk Solids, Sugar, Nutmeg',
            'category': 'SW',
            'product_image': 'product/malaipenda.jpeg'
        },
        {
            'title': 'Mathura Special Penda',
            'selling_price': 480,
            'discounted_price': 440,
            'description': 'Authentic Mathura style penda with a distinct caramelized flavor and texture.',
            'composition': 'Roasted Khoa, Bura Sugar, Ghee, Cardamom',
            'category': 'SW',
            'product_image': 'product/mathurapenda.jpeg'
        },
    ]

    for p_data in penda_products:
        p, created = Product.objects.get_or_create(
            title=p_data['title'],
            defaults=p_data
        )
        if created:
            print(f"Added Sweet: {p.title}")
        else:
            print(f"Product already exists: {p.title}")

if __name__ == "__main__":
    add_penda_products()
