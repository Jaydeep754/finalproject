#!/usr/bin/env python
"""
Debug script to see what HTML is actually rendered
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ec.settings')
django.setup()

from django.test import Client
from app.models import OrderPlaced, DeliveryPerson
from django.conf import settings

if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

delivery_person = DeliveryPerson.objects.first()
order = OrderPlaced.objects.filter(
    delivery_person=delivery_person
).exclude(
    status__in=['Delivered', 'Cancel', 'Failed Delivery']
).first()

if order:
    client = Client()
    response = client.get(f'/delivery-order-detail/{order.id}/', follow=True, HTTP_HOST='testserver')
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Find and print the section with the form
        start = content.find('<div class="update-action-box')
        if start > 0:
            end = content.find('</div>', start) + 6
            section = content[start:end]
            print("UPDATE ACTION BOX SECTION:")
            print(section[:500])
            print("...")
        else:
            # Try to find the order status section
            if 'Current Status' in content:
                print("✓ Found 'Current Status' text")
                idx = content.find('Current Status')
                print(content[max(0, idx-100):idx+400])
            else:
                print("❌ No 'Current Status' found")
                
        # Check if form exists
        if 'deliveryForm' in content:
            print("\n✓ Found deliveryForm ID")
        else:
            print("\n❌ deliveryForm ID not found")
            
        if 'id_status' in content:
            print("✓ Found id_status selector")
        else:
            print("❌ id_status not found")
            
        if 'updateStatusBtn' in content:
            print("✓ Found updateStatusBtn ID")
        else:
            print("❌ updateStatusBtn not found")
            
        # Print total length
        print(f"\n📄 Total HTML length: {len(content)} bytes")
