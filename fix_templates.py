content = """{% extends 'admin_panel/base.html' %}
{% load static %}

{% block title %}
{% if product %}Edit Product{% else %}Add Product{% endif %} - Milk & More Admin
{% endblock %}

{% block page_title %}
{% if product %}Edit Product: {{ product.title }}{% else %}Add New Product{% endif %}
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="glass-card">
            <form method="POST" enctype="multipart/form-data" class="p-2">
                {% csrf_token %}

                <div class="row g-4">
                    <div class="col-md-12 mb-3">
                        <label for="{{ form.title.id_for_label }}" class="form-label fw-bold">Product Title</label>
                        {{ form.title }}
                        {% if form.title.errors %}<div class="text-danger small">{{ form.title.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-6 mb-3">
                        <label for="{{ form.selling_price.id_for_label }}" class="form-label fw-bold">Selling Price (₹)</label>
                        {{ form.selling_price }}
                        {% if form.selling_price.errors %}<div class="text-danger small">{{ form.selling_price.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-6 mb-3">
                        <label for="{{ form.discounted_price.id_for_label }}" class="form-label fw-bold">Discounted Price (₹)</label>
                        {{ form.discounted_price }}
                        {% if form.discounted_price.errors %}<div class="text-danger small">{{ form.discounted_price.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-6 mb-3">
                        <label for="{{ form.category.id_for_label }}" class="form-label fw-bold">Category</label>
                        {{ form.category }}
                        {% if form.category.errors %}<div class="text-danger small">{{ form.category.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-6 mb-3">
                        <label for="{{ form.product_image.id_for_label }}" class="form-label fw-bold">Product Image</label>
                        {{ form.product_image }}
                        {% if form.product_image.errors %}<div class="text-danger small">{{ form.product_image.errors }}</div>{% endif %}
                        {% if product.product_image %}
                        <div class="mt-2">
                            <span class="small text-muted">Current:</span>
                            <img src="{{ product.product_image.url }}" alt="" class="ms-2 rounded" style="width: 50px;">
                        </div>
                        {% endif %}
                    </div>

                    <div class="col-12 mb-3">
                        <label for="{{ form.description.id_for_label }}" class="form-label fw-bold">Description</label>
                        {{ form.description }}
                        {% if form.description.errors %}<div class="text-danger small">{{ form.description.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-6 mb-3">
                        <label for="{{ form.composition.id_for_label }}" class="form-label fw-bold">Composition</label>
                        {{ form.composition }}
                        {% if form.composition.errors %}<div class="text-danger small">{{ form.composition.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-6 mb-3">
                        <label for="{{ form.prodapp.id_for_label }}" class="form-label fw-bold">Product Application</label>
                        {{ form.prodapp }}
                        {% if form.prodapp.errors %}<div class="text-danger small">{{ form.prodapp.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-6 mb-3">
                        <label for="{{ form.quantity.id_for_label }}" class="form-label fw-bold">Available Stock (Quantity)</label>
                        {{ form.quantity }}
                        {% if form.quantity.errors %}<div class="text-danger small">{{ form.quantity.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-6 mb-3">
                        <label for="{{ form.expiry_date.id_for_label }}" class="form-label fw-bold">Expiry Date</label>
                        {{ form.expiry_date }}
                        {% if form.expiry_date.errors %}<div class="text-danger small">{{ form.expiry_date.errors }}</div>{% endif %}
                    </div>
                </div>

                <div class="d-flex justify-content-end gap-3 mt-4">
                    <a href="{% url 'admin-products' %}" class="btn btn-outline-secondary border-2 px-4 rounded-pill">Cancel</a>
                    <button type="submit" class="btn btn-premium px-5 rounded-pill">
                        {% if product %}Update Product{% else %}Add Product{% endif %}
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}"""

customer_content = """{% extends 'admin_panel/base.html' %}
{% load static %}

{% block title %}
{% if customer %}Edit Customer Detail{% else %}Add Customer Detail{% endif %} - Milk & More Admin
{% endblock %}

{% block page_title %}
{% if customer %}Edit Customer: {{ customer.name }}{% else %}Add Customer Detail{% endif %}
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="glass-card">
            <form method="POST" class="p-2">
                {% csrf_token %}

                <div class="row g-4">
                    <div class="col-md-12 mb-3">
                        <label for="{{ form.user.id_for_label }}" class="form-label fw-bold">Select User</label>
                        {{ form.user }}
                        <div class="form-text">Choose the user account this detail belongs to.</div>
                        {% if form.user.errors %}<div class="text-danger small">{{ form.user.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-6 mb-3">
                        <label for="{{ form.name.id_for_label }}" class="form-label fw-bold">Full Name</label>
                        {{ form.name }}
                        {% if form.name.errors %}<div class="text-danger small">{{ form.name.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-6 mb-3">
                        <label for="{{ form.mobile.id_for_label }}" class="form-label fw-bold">Mobile Number</label>
                        {{ form.mobile }}
                        {% if form.mobile.errors %}<div class="text-danger small">{{ form.mobile.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-12 mb-3">
                        <label for="{{ form.locality.id_for_label }}" class="form-label fw-bold">Locality / Address</label>
                        {{ form.locality }}
                        {% if form.locality.errors %}<div class="text-danger small">{{ form.locality.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-4 mb-3">
                        <label for="{{ form.city.id_for_label }}" class="form-label fw-bold">City</label>
                        {{ form.city }}
                        {% if form.city.errors %}<div class="text-danger small">{{ form.city.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-4 mb-3">
                        <label for="{{ form.state.id_for_label }}" class="form-label fw-bold">State</label>
                        {{ form.state }}
                        {% if form.state.errors %}<div class="text-danger small">{{ form.state.errors }}</div>{% endif %}
                    </div>

                    <div class="col-md-4 mb-3">
                        <label for="{{ form.zipcode.id_for_label }}" class="form-label fw-bold">Zipcode</label>
                        {{ form.zipcode }}
                        {% if form.zipcode.errors %}<div class="text-danger small">{{ form.zipcode.errors }}</div>{% endif %}
                    </div>
                </div>

                <div class="d-flex justify-content-end gap-3 mt-4">
                    <a href="{% url 'admin-customers' %}" class="btn btn-outline-secondary border-2 px-4 rounded-pill">Cancel</a>
                    <button type="submit" class="btn btn-premium px-5 rounded-pill">
                        {% if customer %}Update Detail{% else %}Add Detail{% endif %}
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}"""

with open('app/templates/admin_panel/add_product.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open('app/templates/admin_panel/add_customer.html', 'w', encoding='utf-8') as f:
    f.write(customer_content)
