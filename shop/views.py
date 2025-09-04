from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login

from .forms import OrderCreateForm, ContactForm, SignupForm
from .models import Order, Product


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # Send welcome email if user provided an email
            try:
                if user.email:
                    body = (
                        f"Hello {user.username},\n\n"
                        "Welcome to Contact Book!\n\n"
                        "Your registration was successful. You can now log in and start shopping products.\n\n"
                        "Thanks,\n"
                        "eshop Team"
                    )
                    msg = EmailMessage(
                        subject="Registration Successful - Contact Book",
                        body=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[user.email],
                    )
                    msg.send(fail_silently=False)
            except BadHeaderError:
                messages.error(request, "Invalid header in welcome email.")
            except Exception as e:
                # Don't block signup if email fails
                messages.warning(request, f"Signed up, but welcome email failed: {e}")

            messages.success(request, "Welcome! Your account was created.")
            return redirect("order_create")
    else:
        form = SignupForm()

    return render(request, "shop/registration/signup.html", {"form": form})


@login_required
def order_create(request):
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data["product"]
            order = Order(user=request.user, product=product, total_amount=product.price)
            order.save()  # save() also enforces price

            subject = f"Order Confirmation — {order.order_id}"
            message = (
                f"Hi {request.user.username},\n\n"
                f"Thank you for your order!\n"
                f"Product: {product.name}\n"
                f"Order ID: {order.order_id}\n"
                f"Total Amount: ₹{order.total_amount}\n\n"
                f"We'll notify you as your order progresses.\n"
                f"- Team"
            )
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )
                messages.success(request, "Order placed! A confirmation email was sent.")
            except BadHeaderError:
                messages.error(request, "Invalid header found.")
            except Exception as e:
                messages.warning(request, f"Order placed, but email could not be sent: {e}")

            return redirect("order_success", order_id=order.order_id)
    else:
        form = OrderCreateForm()

    # If you're using the CARD UI, pass a queryset (not .values())
    products = Product.objects.filter(is_active=True).order_by("name")

    # If you're still using the dropdown + JS price display, uncomment the next line
    # products = list(Product.objects.filter(is_active=True).order_by("name").values("id", "name", "price"))

    return render(request, "shop/order_create.html", {"form": form, "products": products})


@login_required
def order_success(request, order_id: str):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, "shop/order_success.html", {"order": order})


@login_required
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]
            reply_to = form.cleaned_data.get("email") or request.user.email

            full_message = (
                f"Customer: {request.user.username} (id: {request.user.id})\n"
                f"Reply-To: {reply_to}\n\n"
                f"{message}"
            )
            try:
                send_mail(
                    subject=f"[Customer Query] {subject}",
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL] if isinstance(settings.ADMIN_EMAIL, str) else settings.ADMIN_EMAIL,
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent to the admin.")
                return redirect("order_create")
            except BadHeaderError:
                messages.error(request, "Invalid header found.")
            except Exception as e:
                messages.error(request, f"Could not send your message: {e}")
    else:
        form = ContactForm()

    return render(request, "shop/contact.html", {"form": form})

