from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Order, Product

class OrderCreateForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True).order_by("name"),
        empty_label="Select a product",
        widget=forms.Select(attrs={"class": "form-select", "id": "id_product"}),
        label="Product"
    )

    class Meta:
        model = Order
        fields = ["product"] 

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=120)
    message = forms.CharField(widget=forms.Textarea)
    email = forms.EmailField(required=False, help_text="We'll reply here if needed.")

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
