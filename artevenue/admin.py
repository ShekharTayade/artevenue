from django.contrib import admin
from .models import Order_sms_email, Employee, Profile_group, Business_profile, Publisher
from .models import Publisher_price, Moulding, Promotion, Curated_collection, Egift_card_design
from .models import Egift, eGift_sms_email, Voucher, Voucher_user, Contact_us
from .models import Order, Cart, Curated_category

admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Order_sms_email)
admin.site.register(Employee)
admin.site.register(Profile_group)
admin.site.register(Business_profile)
admin.site.register(Publisher)
admin.site.register(Publisher_price)
admin.site.register(Moulding)
admin.site.register(Promotion)
admin.site.register(Curated_category)
admin.site.register(Curated_collection)
admin.site.register(Egift_card_design)
admin.site.register(Egift)
admin.site.register(eGift_sms_email)
admin.site.register(Voucher)
admin.site.register(Voucher_user)
admin.site.register(Contact_us)

# Register your models here.
