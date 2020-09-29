# Generated by Django 2.2.4 on 2020-09-24 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallerywalls', '0006_remove_gallery_num_of_images'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallery',
            name='wall_area_height',
        ),
        migrations.RemoveField(
            model_name='gallery',
            name='wall_area_width',
        ),
        migrations.AddField(
            model_name='gallery_variation',
            name='wall_area_height',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='gallery_variation',
            name='wall_area_width',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
    ]
