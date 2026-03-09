from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from .forms import LoginForm, MyPasswordResetForm, MyPasswordChangeForm, MySetPasswordForm
from django.contrib import admin

urlpatterns = [

    path("",home,name="home"),
    path("about/",about,name="about"),
    path("contact/",contact,name="contact"),
    path("category/<slug:value>",CategoryView.as_view(),name="category"),
    path("product-detail/<int:pk>",ProductDetail.as_view(),name="product-detail"),
    path("category-title/<value>",CategoryTitle.as_view(),name="category-title"),
    path("profile/",ProfileView.as_view(),name="profile"),
    path("address/",adress,name="address"),
    path("updateAddress/<int:pk>",UpdateAddress.as_view(),name="updateAddress"),
    path("deleteaddress/<int:pk>",delete_address,name = 'deleteaddress'),
    path("add-to-cart/",add_to_cart,name="add_to_cart"),
    path("cart/",showcart,name="showcart"),
    path("checkout/",CheckoutView.as_view(),name="checkout"),
    path("paymentdone/",paymentdone,name='paymentdone'),
    path("checkout-cod/",checkout_cod,name='checkout-cod'),

    path("orders/",orders,name='orders'),
    path("orders/",orders,name='wishlist'),
    path("search/",search,name='search'),

    path("pluscart/",pluscart),
    path("minuscart/",minuscart),
    path("removecart/",removecart),

    # path("pluswishlist/",plus_wishlist),
    # path("minuswishlist/",minus_wishlist),

    #auth
    path("signup/",CustomerRegistrationView.as_view(), name="signup"),
    path("login/", login_user, name='login'), 
    path("passwordchange/", auth_view.PasswordChangeView.as_view(template_name="passwordchange.html", form_class =
    MyPasswordChangeForm,success_url ='/passwordchangedone' ),name="passwordchange"),  
    path("passwordchangedone/", auth_view.PasswordChangeDoneView.as_view(template_name="passwordchangedone.html"),name="passwordchangedone") ,
    path('logout/', Logout, name = 'logout'),

    #custom otp password reset
    path("forgot-password/", forgot_password_view, name="forgot_password"),
    path("verify-otp/", verify_otp_view, name="verify_otp"),
    path("reset-new-password/", reset_new_password_view, name="reset_new_password"),

    # Admin Panel
    path("admin-dashboard/", admin_dashboard, name="admin-dashboard"),
    path("admin-products/", admin_products, name="admin-products"),
    path("admin-add-product/", admin_add_product, name="admin-add-product"),
    path("admin-update-product/<int:pk>/", admin_update_product, name="admin-update-product"),
    path("admin-delete-product/<int:pk>/", admin_delete_product, name="admin-delete-product"),
    path("admin-orders/", admin_orders, name="admin-orders"),
    path("admin-update-order/<int:pk>/", admin_update_order, name="admin-update-order"),
    path("admin-customers/", admin_customers, name="admin-customers"),
    path("admin-add-customer/", admin_add_customer, name="admin-add-customer"),
    path("admin-update-customer/<int:pk>/", admin_update_customer, name="admin-update-customer"),
    path("admin-delete-customer/<int:pk>/", admin_delete_customer, name="admin-delete-customer"),
    path("admin-payments/", admin_payments, name="admin-payments"),
    path("submit-review/<int:product_id>/", submit_review, name="submit-review"),
    path("admin-reviews/", admin_reviews, name="admin-reviews"),
    path("admin-delete-review/<int:pk>/", admin_delete_review, name="admin-delete-review"),
    path("submit-complaint/<int:order_id>/", submit_complaint, name="submit-complaint"),
    path("view-complaints/", view_complaints, name="view-complaints"),
    path("admin-complaints/", admin_complaints, name="admin-complaints"),
    path("admin-reply-complaint/<int:pk>/", admin_reply_complaint, name="admin-reply-complaint"),

    # Delivery Person
    path("delivery-dashboard/", delivery_dashboard, name="delivery-dashboard"),
    path("delivery-orders/", delivery_orders, name="delivery-orders"),
    path("delivery-order-detail/<int:pk>/", delivery_order_detail, name="delivery-order-detail"),
    path("delivery-update-status/<int:pk>/", delivery_update_status, name="delivery-update-status"),
    path("delivery-profile/", delivery_profile, name="delivery-profile"),
    
    # Admin - Delivery Person Management
    path("admin-delivery-persons/", admin_delivery_persons, name="admin-delivery-persons"),
    path("admin-add-delivery-person/", admin_add_delivery_person, name="admin-add-delivery-person"),
    path("admin-update-delivery-person/<int:pk>/", admin_update_delivery_person, name="admin-update-delivery-person"),
    path("admin-delete-delivery-person/<int:pk>/", admin_delete_delivery_person, name="admin-delete-delivery-person"),
    path("admin-assign-order/<int:pk>/", admin_assign_order, name="admin-assign-order"),

    # Invoice Generation
    path("download-invoice/<int:payment_id>/", download_invoice, name="download-invoice"),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Milk & More"
admin.site.site_title = "Milk & More Administration"
admin.site.site_index_title = "Welcome to Milk & More"


