# Generated by Django 2.2.4 on 2019-11-18 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artevenue', '0066_auto_20191111_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='ip_address',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
