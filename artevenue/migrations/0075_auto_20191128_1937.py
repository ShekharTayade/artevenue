# Generated by Django 2.2.4 on 2019-11-28 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artevenue', '0074_auto_20191128_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='original_art',
            name='art_surface',
            field=models.CharField(blank=True, choices=[('CVS', 'CANVAS'), ('PPR', 'PAPER'), ('FAB', 'FABRIC'), ('GLS', 'GLASS'), ('WOD', 'WOOD')], default='', max_length=3),
        ),
    ]
