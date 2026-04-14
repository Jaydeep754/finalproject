# Generated migration for adding viewed_by_admin field to Customer, Payment, and DeliveryPerson

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_productreview_viewed_by_admin_complaint_viewed_by_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='viewed_by_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='payment',
            name='viewed_by_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='deliveryperson',
            name='viewed_by_admin',
            field=models.BooleanField(default=False),
        ),
    ]
