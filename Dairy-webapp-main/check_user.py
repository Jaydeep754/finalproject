import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ec.settings')
django.setup()

from django.contrib.auth.models import User

user = User.objects.filter(username='milkmore').first()
if user: 
    print(f"User: {user.username}")
    print(f"is_staff: {user.is_staff}")
    print(f"is_superuser: {user.is_superuser}")
else:
    print("User milkmore not found")
