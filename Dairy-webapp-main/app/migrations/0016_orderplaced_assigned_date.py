# Generated migration for adding assigned_date field to OrderPlaced

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_customer_viewed_by_admin_payment_viewed_by_admin_deliveryperson_viewed_by_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderplaced',
            name='assigned_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
