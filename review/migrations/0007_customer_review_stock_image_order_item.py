# Generated by Django 2.2.4 on 2020-07-02 03:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('artevenue', '0112_auto_20200702_0904'),
        ('review', '0006_customer_review_stock_image_pics_disp_seq'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer_review_stock_image_order_item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_review_stock_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='review.Customer_review_stock_image')),
                ('order_stock_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='artevenue.Order_stock_image')),
            ],
        ),
    ]
