# Generated by Django 2.2.4 on 2019-09-06 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artevenue', '0049_auto_20190829_1033'),
    ]

    operations = [
        migrations.AddField(
            model_name='original_art',
            name='category_disp_priority',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='stock_collage',
            name='category_disp_priority',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='stock_image',
            name='category_disp_priority',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='user_image',
            name='category_disp_priority',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='original_art',
            name='art_medium',
            field=models.CharField(blank=True, choices=[('OIL', 'Oil'), ('ACR', 'Acrylic'), ('WTR', 'Water Color'), ('GOU', 'Gouache'), ('INK', 'Ink'), ('PEN', 'Pen'), ('PST', 'Pastel'), ('PNC', 'Pencil'), ('COL', 'Charcoal')], default='', max_length=3),
        ),
        migrations.AlterField(
            model_name='original_art',
            name='art_surface',
            field=models.CharField(blank=True, choices=[('CVS', 'CANVAS'), ('PPR', 'PAPER'), ('FAB', 'FABRIC'), ('GLS', 'GLASS'), ('WOD', 'WOOD')], default='', max_length=3),
        ),
        migrations.AlterField(
            model_name='original_art',
            name='image_type',
            field=models.CharField(choices=[('ART', 'Art Work'), ('PHT', 'Photograph')], max_length=1, null=True),
        ),
    ]
