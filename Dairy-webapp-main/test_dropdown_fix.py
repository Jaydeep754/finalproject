#!/usr/bin/env python
"""
Test script to verify delivery order dropdown and update button work together
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ec.settings')
django.setup()

from django.test import Client
from app.models import OrderPlaced, DeliveryPerson

def test_delivery_dropdown():
    """Test that the delivery order dropdown is functional"""
    
    try:
        # Get a delivery person with pending orders
        delivery_person = DeliveryPerson.objects.first()
        if not delivery_person:
            print("❌ No delivery person found")
            return False
        
        # Get a pending order for this delivery person
        order = OrderPlaced.objects.filter(
            delivery_person=delivery_person
        ).exclude(
            status__in=['Delivered', 'Cancel', 'Failed Delivery']
        ).first()
        
        if not order:
            print("❌ No pending orders found for test")
            return False
        
        print(f"✓ Found order #{order.id} with status '{order.status}'")
        
        # Test the template rendering
        client = Client()
        
        # Add testserver to allowed hosts temporarily
        from django.conf import settings
        if 'testserver' not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS.append('testserver')
        
        url = f'/delivery-order-detail/{order.id}/'
        print(f"\nTesting URL: {url}")
        
        response = client.get(url, follow=True, HTTP_HOST='testserver')
        
        if response.status_code != 200:
            print(f"❌ Page failed to load (Status: {response.status_code})")
            return False
        
        print(f"✓ Page loaded successfully (Status: {response.status_code})")
        
        # Check for required HTML elements
        content = response.content.decode('utf-8')
        
        required_elements = [
            ('id="id_status"', 'Status dropdown select element'),
            ('id="updateStatusBtn"', 'Update button element'),
            ('<select', 'HTML select tag'),
            ('<button', 'HTML button tag'),
            ('form-select', 'Bootstrap select styling'),
            ('btn-primary', 'Bootstrap button styling'),
        ]
        
        print("\n✓ Checking for required HTML elements:")
        all_present = True
        for element, description in required_elements:
            if element in content:
                print(f"  ✓ {description}")
            else:
                print(f"  ❌ {description} - MISSING")
                all_present = False
        
        # Check JavaScript functionality
        js_checks = [
            ('updateStatusBtn.addEventListener', 'Setup button click listener'),
            ('statusSelect.value', 'Read dropdown value'),
            ('fetch(', 'Send AJAX request'),
            ('DOMContentLoaded', 'Wait for DOM ready'),
            ('showSuccessNotification', 'Success notification function'),
            ('showErrorNotification', 'Error notification function'),
        ]
        
        print("\n✓ Checking for JavaScript functionality:")
        js_ok = True
        for check, description in js_checks:
            if check in content:
                print(f"  ✓ {description}")
            else:
                print(f"  ❌ {description} - MISSING")
                js_ok = False
        
        # Check for syntax errors in JavaScript
        if 'AbortSignal.timeout' in content:
            print("\n⚠️  WARNING: Found AbortSignal.timeout which may not be supported in all browsers")
        else:
            print("\n✓ No unsupported AbortSignal.timeout found")
        
        if all_present and js_ok:
            print("\n✅ ALL CHECKS PASSED!")
            print("\nThe dropdown should now be working properly. You can:")
            print("  1. Click the status dropdown to change the status")
            print("  2. Click the Update button to send the new status")
            print("  3. See success/error messages appear as toast notifications")
            return True
        else:
            print("\n⚠️  Some elements or functions are missing")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_delivery_dropdown()
    sys.exit(0 if success else 1)
