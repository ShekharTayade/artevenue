from django.contrib.auth.models import User, Group
from rest_framework import serializers
from artevenue.models import Stock_image, Stock_image_category
from artevenue.models import Homelane_data, Publisher, Moulding
		
		
class Stock_image_categorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Stock_image_category
        fields = ['category_id', 'name']		

class MouldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moulding
        fields = ['moulding_id', 'name', 'width', 'depth', 'applies_to']
		
		
class Homelane_dataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homelane_data
        fields = ['product_id', 'product_name', 'product_type', 'is_published',
			'category_name', 'aspect_ratio', 'image_type', 'orientation', 
			'image_width', 'image_height', 'artist', 'key_words', 'moulding_name',
			'print_medium_name', 'mount_name', 'mount_size',
			'framed_url', 'framed_thumbnail_url', 'item_unit_price', 'item_sub_total',
			'item_disc_amt', 'item_tax', 'item_total']
