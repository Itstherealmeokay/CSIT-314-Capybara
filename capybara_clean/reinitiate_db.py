import os
import django
from django.contrib.auth import get_user_model

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "capybara_clean.settings")
django.setup()

from webapp.models import *

dev_users = {
    'superusers': [
        {'username': 'Jux', 'email': 'Juxarius@example.com', 'password': '123', 'role': 'admin'},
    ],
    'homeowners': [
        {'username': 'Juxaxa', 'email': 'Juxarius@example.com', 'password': '123', 'role': 'homeowner'},
    ],
    'cleaners': [
        {'username': 'Juxy', 'email': 'Juxarius@example.com', 'password': '123', 'role': 'cleaner'},
    ],
}

def register_users():
    User = get_user_model()
    for su in dev_users['superusers']:
        if not User.objects.filter(username=su['username']).exists():
            User.objects.create_superuser(**su)
    for ho in dev_users['homeowners']:
        if not User.objects.filter(username=ho['username']).exists():
            User.objects.create_user(**ho)
            Homeowner.objects.create(user=User.objects.get(username=ho['username']))
    for cl in dev_users['cleaners']:
        if not User.objects.filter(username=cl['username']).exists():
            User.objects.create_user(**cl)
            Cleaner.objects.create(user=User.objects.get(username=cl['username']))

if __name__ == "__main__":
    register_users()