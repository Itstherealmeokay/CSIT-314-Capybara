# Generated by Django 5.2 on 2025-05-01 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0018_remove_cleaninglisting_requests'),
    ]

    operations = [
        migrations.AddField(
            model_name='cleaninglisting',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
