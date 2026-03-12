import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ec.settings')
django.setup()

from app.models import Product

# Create a test product
p = Product.objects.create(
    title="Test Product for Deletion",
    selling_price=100,
    discounted_price=80,
    description="Test",
    composition="Test",
    category="MK"
)
print(f"Created product with ID: {p.id}")

# Delete it
p_id = p.id
p.delete()
print(f"Deleted product with ID: {p_id}")

# Verify
exists = Product.objects.filter(id=p_id).exists()
print(f"Exists after deletion: {exists}")
