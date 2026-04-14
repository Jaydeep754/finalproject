#!/usr/bin/env python
"""
Test script to verify the delivery order update button is working
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ec.settings')
django.setup()

from app.models import OrderPlaced, DeliveryPerson, Customer
from django.contrib.auth.models import User

# Get or create test data
try:
    # Get a delivery person
    delivery_person = DeliveryPerson.objects.first()
    if not delivery_person:
        print("❌ No delivery person found in database")
        exit(1)
    
    # Get an order assigned to this delivery person
    order = OrderPlaced.objects.filter(delivery_person=delivery_person).exclude(status='Delivered').exclude(status='Cancel').exclude(status='Failed Delivery').first()
    
    if not order:
        print(f"❌ No pending orders found for delivery person {delivery_person.name}")
        # Create a test order if none exists
        customer = Customer.objects.first()
        if customer:
            from django.utils import timezone
            from app.models import Payment
            
            payment = Payment.objects.create(
                amount=500,
                razorpay_payment_status='Cash On Delivery',
                paid=False
            )
            
            order = OrderPlaced.objects.create(
                customer=customer,
                payment=payment,
                delivery_person=delivery_person,
                status='Assigned',
                delivery_date='2026-04-15'
            )
            print(f"✓ Created test order #{order.id}")
        else:
            print("❌ No customers found in database")
            exit(1)
    else:
        print(f"✓ Found order #{order.id} with status '{order.status}'")
    
    # Test the template rendering
    from django.test import Client
    client = Client()
    
    # Try to access the delivery order detail page
    url = f'/delivery/order/{order.id}/'
    print(f"\nTesting URL: {url}")
    
    response = client.get(url, follow=True)
    
    if response.status_code == 200:
        print(f"✓ Page loaded successfully (Status: {response.status_code})")
        
        # Check if required JavaScript elements are in the page
        content = response.content.decode('utf-8')
        
        checks = [
            ('id="updateStatusBtn"', 'Update button element'),
            ('id="id_status"', 'Status select element'),
            ('id="deliveryForm"', 'Delivery form'),
            ('updateStatusBtn.addEventListener', 'Update button event listener'),
            ('showSuccessNotification', 'Success notification function'),
            ('showErrorNotification', 'Error notification function'),
        ]
        
        print("\n✓ Template Element Checks:")
        all_passed = True
        for check_str, description in checks:
            if check_str in content:
                print(f"  ✓ Found: {description}")
            else:
                print(f"  ❌ Missing: {description}")
                all_passed = False
        
        # Check for JavaScript syntax errors
        if 'fetch(' in content and 'DOMContentLoaded' in content:
            print("\n✓ JavaScript framework present")
        
        if all_passed:
            print("\n✅ All checks passed! The button should be clickable.")
        else:
            print("\n⚠️  Some elements are missing. Please check the template.")
    else:
        print(f"❌ Page failed to load (Status: {response.status_code})")
        if response.status_code == 302:
            print(f"   Redirected to: {response.url}")
        print(f"   Content: {response.content[:200]}")
        
except Exception as e:
    print(f"❌ Error occurred: {str(e)}")
    import traceback
    traceback.print_exc()
