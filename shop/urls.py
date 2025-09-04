from django.urls import path
from . import views
urlpatterns = [
    path("", views.order_create, name="order_create"),
    path("order/success/<str:order_id>/", views.order_success, name="order_success"),
    path("contact/", views.contact, name="contact"),
    path("accounts/signup/", views.signup, name="signup"),
]