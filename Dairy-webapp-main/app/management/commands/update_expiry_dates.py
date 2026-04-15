from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta
from app.models import Product

class Command(BaseCommand):
    help = 'Update product expiry dates based on shelf life'

    def handle(self, *args, **options):
        today = now().date()
        
        # Define shelf life in days for each product category
        shelf_life = {
            'MK': 2,   # Milk - 2 days
            'LS': 3,   # Lassi - 3 days
            'BS': 4,   # Basundi - 4 days
            'MT': 3,   # Matho - 3 days
            'SW': 7,   # Sweets - 7 days
            'IC': 180, # Ice cream - 6 months (180 days)
        }
        
        updated_count = 0
        
        for category_code, days in shelf_life.items():
            expiry_date = today + timedelta(days=days)
            products = Product.objects.filter(category=category_code)
            
            for product in products:
                product.expiry_date = expiry_date
                product.save()
                updated_count += 1
                
                category_name = dict(product._meta.get_field('category').choices).get(category_code)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Updated {product.title} ({category_name}) - Expiry: {expiry_date}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Successfully updated {updated_count} products!')
        )
