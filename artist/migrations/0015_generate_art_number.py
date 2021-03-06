# Generated by Django 2.2.4 on 2020-09-08 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0014_delete_generate_art_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Generate_art_number',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publisher', models.CharField(max_length=20)),
                ('type', models.CharField(choices=[('PART', 'Part Number'), ('ORIG', 'Original ID'), ('STKI', 'Stock Image ID')], max_length=4)),
                ('prefix', models.CharField(max_length=10)),
                ('suffix', models.CharField(default='', max_length=10)),
                ('current_number', models.IntegerField()),
            ],
        ),
    ]
