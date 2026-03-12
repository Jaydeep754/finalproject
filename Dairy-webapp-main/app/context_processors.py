from .models import Customer

def regional_restriction(request):
    """
    Checks if the authenticated user has any addresses in Ahmedabad.
    Provides 'is_in_ahmedabad' to all templates.
    """
    is_delivery = hasattr(request.user, 'deliveryperson')
    if request.user.is_authenticated and not request.user.is_staff and not is_delivery:
        # Check if the user has any customer profile (address) and if none are in Ahmedabad
        has_addresses = Customer.objects.filter(user=request.user).exists()
        in_ahmedabad = Customer.objects.filter(user=request.user, city__iexact='Ahmedabad').exists()
        
        # We only want to show the overlay if they HAVE addresses but NONE of them are Ahmedabad
        show_restricted_overlay = has_addresses and not in_ahmedabad
        
        return {
            'is_in_ahmedabad': in_ahmedabad,
            'has_any_address': has_addresses,
            'show_restricted_overlay': show_restricted_overlay
        }
    return {
        'is_in_ahmedabad': True, # Default to True for guests/staff to avoid blocking
        'has_any_address': False,
        'show_restricted_overlay': False
    }
