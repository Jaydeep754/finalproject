import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ec.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin_user():
    username = 'milkmore'
    password = 'milkmore1234'
    email = 'admin@milkmore.com'

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully!")
    else:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f"User '{username}' already exists. Password updated and permissions granted.")

if __name__ == '__main__':
    create_admin_user()
