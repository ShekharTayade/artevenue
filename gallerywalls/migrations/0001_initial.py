# Generated by Django 2.2.4 on 2020-09-19 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('artevenue', '0124_auto_20200919_1736'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('gallery_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=1000, null=True)),
                ('num_of_images', models.IntegerField()),
                ('wall_area_width', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('wall_area_height', models.DecimalField(decimal_places=2, max_digits=6, null=True)),
                ('room_view_url', models.CharField(max_length=1000, null=True)),
                ('set_of', models.IntegerField(null=True)),
                ('category_disp_priority', models.IntegerField(null=True)),
                ('is_published', models.BooleanField(default=False)),
                ('colors', models.CharField(max_length=600, null=True)),
                ('key_words', models.CharField(max_length=2000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('room_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Placement',
            fields=[
                ('placement_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('room', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gallerywalls.Room')),
            ],
        ),
        migrations.CreateModel(
            name='Gallery_item',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('product_id', models.IntegerField()),
                ('moulding_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('mount_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('image_width', models.DecimalField(decimal_places=0, max_digits=3)),
                ('image_height', models.DecimalField(decimal_places=0, max_digits=3)),
                ('acrylic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Acrylic')),
                ('board', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Board')),
                ('gallery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gallerywalls.Gallery')),
                ('moulding', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Moulding')),
                ('mount', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Mount')),
                ('print_medium', models.ForeignKey(default='PAPER', on_delete=django.db.models.deletion.PROTECT, to='artevenue.Print_medium')),
                ('product_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='artevenue.Product_type')),
                ('stretch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Stretch')),
            ],
        ),
        migrations.AddField(
            model_name='gallery',
            name='placement',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gallerywalls.Placement'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='room',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gallerywalls.Room'),
        ),
        migrations.AddField(
            model_name='gallery',
            name='stock_image_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='artevenue.Stock_image_category'),
        ),
    ]
