# Generated manually to update box size choices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boardshipper', '0002_booking_easypost_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='box_size',
            field=models.CharField(choices=[('shortboard', 'Shortboard'), ('midlength', 'Midlength'), ('longboard', 'Longboard')], max_length=10),
        ),
    ]