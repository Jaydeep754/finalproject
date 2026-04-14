from .models import Customer, OrderPlaced, ProductReview, Complaint, Payment

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

def admin_notifications(request):
    """
    Provides notification counts for admin panel sidebar badges.
    Counts: pending orders, product reviews, pending complaints, new customers, new payments, sales reports.
    Only shows counts if the notification hasn't been marked as "seen" in the session.
    """
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        # Get from session which notifications have been "seen"
        seen_notifications = request.session.get('seen_notifications', {})
        
        # Get all notification counts
        pending_orders_count = OrderPlaced.objects.filter(status='Pending').count() if not seen_notifications.get('orders') else 0
        reviews_count = ProductReview.objects.count() if not seen_notifications.get('reviews') else 0
        pending_complaints_count = Complaint.objects.filter(status='Pending').count() if not seen_notifications.get('complaints') else 0
        new_customers_count = Customer.objects.filter(user__date_joined__gte=request.session.get('last_admin_visit', '2000-01-01')).count() if 'last_admin_visit' not in request.session and not seen_notifications.get('customers') else 0
        new_payments_count = Payment.objects.filter(paid=False).count() if not seen_notifications.get('payments') else 0
        
        return {
            'pending_orders_count': pending_orders_count,
            'reviews_count': reviews_count,
            'pending_complaints_count': pending_complaints_count,
            'new_customers_count': new_customers_count,
            'new_payments_count': new_payments_count,
            'seen_notifications': seen_notifications,
        }
    return {
        'pending_orders_count': 0,
        'reviews_count': 0,
        'pending_complaints_count': 0,
        'new_customers_count': 0,
        'new_payments_count': 0,
        'seen_notifications': {},
    }
