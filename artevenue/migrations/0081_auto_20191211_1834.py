# Generated by Django 2.2.4 on 2019-12-11 13:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('artevenue', '0080_order_channel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='channel_order_amz',
            old_name='arteveue_order_no',
            new_name='order',
        ),
    ]
