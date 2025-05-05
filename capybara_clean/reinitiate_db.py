import os
import django
import json
from django.contrib.auth import get_user_model
import random
import datetime as dt

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "capybara_clean.settings")
django.setup()
data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "initiate_db_data.json")

from webapp.models import *

USER_FIELDS = ['username', 'password', 'email']

with open(data_file, 'r') as f:
    dev_users = json.load(f)

def register_users():
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
    for pm in dev_users['platform_managers']:
        if not User.objects.filter(username=pm['username']).exists():
            d1, d2 = break_apart(pm)
            user = User.objects.create_user(role='platform_manager', **d1)
            PlatformManager.objects.create(user=user, **d2)
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

    for category in dev_users['service_categories']:
        if not ServiceCategory.objects.filter(name=category).exists():
            ServiceCategory.objects.create(name=category)

    jux_min_property = 5
    for idx, property in enumerate(dev_users['properties']):
        if not Property.objects.filter(address=property['address']).exists():
            if idx < jux_min_property:
                the_chosen_one = 'Juxaxa'
            else:
                the_chosen_one = random.choice(dev_users['homeowners'])['username']
            Property.objects.create(**property, homeowner=Homeowner.objects.get(user__username=the_chosen_one))

def add_cleaning_listing(num_cleaners=10):
    cleaners = list(Cleaner.objects.all())
    service_categories = list(ServiceCategory.objects.all())
    chosen_cleaners = random.sample(cleaners, num_cleaners) + list(Cleaner.objects.filter(user__username='Juxy'))
    for cleaner in chosen_cleaners:
        for cleaning_listing in random.sample(dev_users['cleaning_listings'], random.randint(1, 4)):
            CleaningListing.objects.create(**cleaning_listing, cleaner=cleaner, service_category=random.choice(service_categories))

def add_cleaning_requests():
    properties = list(Property.objects.all())
    
    cleaning_listings = list(CleaningListing.objects.all())
    for listing in random.sample(cleaning_listings, random.randint(1, len(cleaning_listings))):
        CleaningRequest.objects.create(
            cleaning_listing=listing, 
            property=random.choice(properties),
            status=random.choice(CleaningRequestStatus.choices)[0],
            request_date=dt.datetime.now() + dt.timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59)),
        )

if __name__ == "__main__":
    # register_users()
    # add_cleaning_listing()
    add_cleaning_requests()