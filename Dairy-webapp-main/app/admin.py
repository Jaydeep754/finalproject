from django.contrib import admin
from .models import Product, Customer,Cart,Payment,OrderPlaced, ProductReview, Complaint, DeliveryPerson

@admin.register(DeliveryPerson)
class DeliveryPersonModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'mobile', 'is_active']

@admin.register(ProductReview)
class ProductReviewModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'rating', 'created_at']
from django.utils.html import format_html
from django.urls import reverse
# Register your models here.

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'discounted_price', 'category','product_image']

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','locality','city','state','state','zipcode']

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','products','quantity']
    def products(self,obj):
        link = reverse("admin:app_product_change",args=[obj.product.pk])
        return format_html('<a href="{}">{}</a>',link, obj.product.title)

@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display=['id','user','amount','razorpay_order_id','razorpay_payment_status','razorpay_payment_id','paid']

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display =['id','user','customer','product','quantity','ordered_date','status','payment', 'delivery_person']

@admin.register(Complaint)
class ComplaintModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order', 'subject', 'status', 'created_at']



