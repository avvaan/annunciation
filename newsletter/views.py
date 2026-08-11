from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import SubscribeForm
from .models import Subscriber


def subscribe(request):
    if request.method == "POST":
        form = SubscribeForm(request.POST)
        if form.is_valid():
            subscriber, _ = Subscriber.objects.update_or_create(
                email=form.cleaned_data["email"],
                defaults={"name": form.cleaned_data["name"]},
            )
            confirm_url = request.build_absolute_uri(
                reverse("newsletter:confirm", args=[subscriber.confirmation_token])
            )
            send_mail(
                "Подтвердите подписку на новости прихода",
                f"Чтобы подтвердить подписку, перейдите по ссылке: {confirm_url}",
                None,
                [subscriber.email],
                fail_silently=True,
            )
            messages.success(request, "Проверьте почту — мы отправили письмо для подтверждения подписки.")
            return redirect("newsletter:subscribe")
    else:
        form = SubscribeForm()
    return render(request, "newsletter/subscribe.html", {"form": form})


def confirm(request, token):
    subscriber = get_object_or_404(Subscriber, confirmation_token=token)
    subscriber.is_active = True
    subscriber.confirmed_at = timezone.now()
    subscriber.save(update_fields=["is_active", "confirmed_at"])
    messages.success(request, "Подписка подтверждена. Спасибо!")
    return redirect("newsletter:subscribe")


def unsubscribe(request, token):
    subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)
    subscriber.is_active = False
    subscriber.save(update_fields=["is_active"])
    messages.info(request, "Вы отписаны от рассылки.")
    return redirect("newsletter:subscribe")
