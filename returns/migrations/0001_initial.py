# Generated by Django 2.2.4 on 2021-02-22 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('artevenue', '0130_auto_20210113_1532'),
    ]

    operations = [
        migrations.CreateModel(
            name='Credit_note',
            fields=[
                ('crn_id', models.AutoField(primary_key=True, serialize=False)),
                ('credit_note_number', models.CharField(blank=True, default='', max_length=15)),
                ('credit_note_date', models.DateTimeField(null=True)),
                ('credit_note_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('credit_note_reason', models.CharField(blank=True, choices=[('UN', 'Not Specified'), ('RT', 'Full Refund Issued for Customer Return'), ('DM', 'Full Refund Issued for Damaged Delivery'), ('PR', 'Partial Refund for Damaged Delivery'), ('PC', 'Partial Refund for Customer Return'), ('CA', 'Reduced Price Due to Changes to Artwork'), ('RM', 'Artwork Removed from the Order'), ('AD', 'Additional Discount Offered'), ('CN', 'Order Cancelled')], default='', max_length=2)),
                ('remarks', models.CharField(blank=True, default='', max_length=500)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='artevenue.Order')),
            ],
        ),
        migrations.CreateModel(
            name='Debit_note',
            fields=[
                ('drn_id', models.AutoField(primary_key=True, serialize=False)),
                ('debit_note_number', models.CharField(blank=True, default='', max_length=15)),
                ('debit_note_date', models.DateTimeField(null=True)),
                ('debit_note_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('debit_note_reason', models.CharField(blank=True, choices=[('UN', 'Not Specified'), ('CA', 'Increased Price Due to Changes to Artwork'), ('AA', 'Additional Artwork Added to the Order'), ('AF', 'Increased Price Due to Additional Framing'), ('OT', 'Increased Price Due to Other Changes')], default='', max_length=2)),
                ('remarks', models.CharField(blank=True, default='', max_length=500)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='artevenue.Order')),
            ],
        ),
        migrations.CreateModel(
            name='Return_order',
            fields=[
                ('ret_id', models.AutoField(primary_key=True, serialize=False)),
                ('ret_number', models.CharField(blank=True, default='', max_length=15)),
                ('ret_request_date', models.DateTimeField(null=True)),
                ('ret_reason', models.CharField(blank=True, choices=[('UN', 'Not Specified'), ('Q', 'Quality Issue'), ('D', 'Damaged Delivery'), ('S', 'Size Issue'), ('N', "Don't Need It"), ('L', 'Did not Like It')], default='', max_length=2)),
                ('return_shipment_charges', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('other_deductions', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total_deductions', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('refund_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('refund_transaction_reference', models.CharField(blank=True, default='', max_length=500)),
                ('remarks', models.CharField(blank=True, default='', max_length=500)),
                ('ret_process_date', models.DateTimeField(null=True)),
                ('ret_status', models.CharField(blank=True, choices=[('RQ', 'Return Request Raised'), ('IN', 'Return Request Being Processed'), ('SH', 'Return Shipment Booked'), ('PK', 'Return Shipment Picked Up'), ('RC', 'Return Shipment Received by ArteVenue'), ('QC', 'Quality Check In Process'), ('QF', 'Quality Check Failed'), ('QP', 'Quality Check Passed'), ('RI', 'Refund Issued')], default='PP', max_length=2)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='artevenue.Order')),
                ('ret_shipper', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Shipper')),
                ('ret_shipping_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Shipping_method')),
                ('ret_shipping_status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Shipping_status')),
            ],
        ),
        migrations.CreateModel(
            name='Return_order_item',
            fields=[
                ('ret_item_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_item_id', models.IntegerField()),
                ('ret_item_quantity', models.IntegerField()),
                ('ret_item_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('ret_item_sub_total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('ret_item_disc_amt', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('ret_item_tax', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('ret_item_total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('quality_check_date', models.DateTimeField(null=True)),
                ('quality_check_passed', models.BooleanField(default=False, null=True)),
                ('quality_check_failed_reason', models.CharField(blank=True, choices=[('DM', 'Products Received in Damanged Condition'), ('WR', 'Products Received Are Not As Per The Order')], default='', max_length=2)),
                ('return_order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='returns.Return_order')),
            ],
        ),
        migrations.CreateModel(
            name='Debit_note_detail',
            fields=[
                ('drn_detail_id', models.AutoField(primary_key=True, serialize=False)),
                ('product_id', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('item_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('item_sub_total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('item_disc_amt', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('item_tax', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('item_total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('moulding_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('print_medium_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('mount_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('board_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('acrylic_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('stretch_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('image_width', models.DecimalField(decimal_places=0, max_digits=3)),
                ('image_height', models.DecimalField(decimal_places=0, max_digits=3)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('acrylic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Acrylic')),
                ('board', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Board')),
                ('debit_note', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='returns.Debit_note')),
                ('moulding', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Moulding')),
                ('mount', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Mount')),
                ('print_medium', models.ForeignKey(default='PAPER', on_delete=django.db.models.deletion.PROTECT, to='artevenue.Print_medium')),
                ('product_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='artevenue.Product_type')),
                ('promotion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Promotion')),
                ('stretch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Stretch')),
            ],
        ),
        migrations.CreateModel(
            name='Credit_note_detail',
            fields=[
                ('crn_detail_id', models.AutoField(primary_key=True, serialize=False)),
                ('product_id', models.IntegerField()),
                ('quantity', models.IntegerField()),
                ('item_unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('item_sub_total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('item_disc_amt', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('item_tax', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('item_total', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('moulding_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('print_medium_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('mount_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('board_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('acrylic_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('stretch_size', models.DecimalField(decimal_places=2, max_digits=12, null=True)),
                ('image_width', models.DecimalField(decimal_places=0, max_digits=3)),
                ('image_height', models.DecimalField(decimal_places=0, max_digits=3)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('acrylic', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Acrylic')),
                ('board', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Board')),
                ('credit_note', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='returns.Credit_note')),
                ('moulding', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Moulding')),
                ('mount', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Mount')),
                ('print_medium', models.ForeignKey(default='PAPER', on_delete=django.db.models.deletion.PROTECT, to='artevenue.Print_medium')),
                ('product_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='artevenue.Product_type')),
                ('promotion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Promotion')),
                ('stretch', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='artevenue.Stretch')),
            ],
        ),
    ]
