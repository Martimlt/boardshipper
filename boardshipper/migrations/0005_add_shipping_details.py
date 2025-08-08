# Generated manually to add shipping carrier details

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boardshipper', '0004_add_recipient_contact_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='shipping_carrier',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='shipping_service',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='shipping_rate',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]