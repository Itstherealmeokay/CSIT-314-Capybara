import os
import django
import json
from django.contrib.auth import get_user_model

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "capybara_clean.settings")
django.setup()
data_file = 'D:\Coding Projects\For-Chingz\CSIT314\CSIT-314-Capybara\capybara_clean\initiate_db_data.json'

from webapp.models import *

USER_FIELDS = ['username', 'password', 'email']

def register_users():
    with open(data_file, 'r') as f:
        dev_users = json.load(f)
    User = get_user_model()
    def break_apart(user_data):
        d1, d2 = {}, {}
        for k,v in user_data.items():
            if k in USER_FIELDS: d1[k] = v
            else: d2[k] = v
        return d1, d2
    for su in dev_users['superusers']:
        if not User.objects.filter(username=su['username']).exists():
            d1, d2 = break_apart(su)
            user = User.objects.create_superuser(role='admin', **d1)
            UserProfile.objects.create(user=user, **d2)
    for ho in dev_users['homeowners']:
        if not User.objects.filter(username=ho['username']).exists():
            d1, d2 = break_apart(ho)
            user = User.objects.create_user(role='homeowner', **d1)
            Homeowner.objects.create(user=user, **d2)
    for cl in dev_users['cleaners']:
        if not User.objects.filter(username=cl['username']).exists():
            d1, d2 = break_apart(cl)
            user = User.objects.create_user(role='cleaner', **d1)
            Cleaner.objects.create(user=user, **d2)

if __name__ == "__main__":
    register_users()