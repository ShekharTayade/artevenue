# Generated by Django 2.2.4 on 2020-09-22 10:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('artevenue', '0124_auto_20200919_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile_group',
            name='flat_or_slab',
            field=models.CharField(choices=[('F', 'Flat Discount or referral fee percentage'), ('S', 'Discount or referral fee percentage based on slabs of order volumes')], default='F', max_length=1),
        ),
        migrations.AddField(
            model_name='profile_group',
            name='profile_type',
            field=models.CharField(choices=[('D', 'Discount on every order'), ('R', 'Referral fee for every order')], default='D', max_length=1),
        ),
        migrations.CreateModel(
            name='Referral_slab',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slab_name', models.CharField(blank=True, max_length=30)),
                ('rule', models.CharField(blank=True, max_length=500)),
                ('min_amt', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('max_amt', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('percentage', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('product_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='artevenue.Product_type')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='artevenue.Profile_group')),
            ],
        ),
        migrations.CreateModel(
            name='Discount_slab',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slab_name', models.CharField(blank=True, max_length=30)),
                ('rule', models.CharField(blank=True, max_length=500)),
                ('min_amt', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('max_amt', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('product_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='artevenue.Product_type')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='artevenue.Profile_group')),
                ('voucher', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Voucher')),
            ],
        ),
        migrations.CreateModel(
            name='Discount_flat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30)),
                ('rule', models.CharField(blank=True, max_length=500)),
                ('product_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='artevenue.Product_type')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='artevenue.Profile_group')),
                ('voucher', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Voucher')),
            ],
        ),
    ]
