# Generated by Django 2.2.4 on 2022-01-12 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('av_products', '0006_cart_round_artwork_order_round_artwork'),
    ]

    operations = [
        migrations.AddField(
            model_name='av_product',
            name='display_url',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
    ]
