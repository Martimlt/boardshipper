# Generated manually for EasyPost integration fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boardshipper', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='label_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='tracking_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='easypost_shipment_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]