# Generated by Django 2.1.4 on 2019-05-05 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artevenue', '0017_auto_20190505_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='egift_card_design',
            name='location',
            field=models.CharField(blank=True, default='', max_length=128),
        ),
    ]
