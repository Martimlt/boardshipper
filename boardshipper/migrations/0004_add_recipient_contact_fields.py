# Generated manually to add recipient email and phone fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boardshipper', '0003_update_box_size_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='recipient_email',
            field=models.EmailField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='booking',
            name='recipient_phone',
            field=models.CharField(default='', max_length=20),
            preserve_default=False,
        ),
    ]