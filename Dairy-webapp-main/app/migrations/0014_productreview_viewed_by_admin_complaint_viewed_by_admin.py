# Generated migration for adding viewed_by_admin field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_orderplaced_delivery_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='productreview',
            name='viewed_by_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='complaint',
            name='viewed_by_admin',
            field=models.BooleanField(default=False),
        ),
    ]
