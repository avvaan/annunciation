import uuid

from django.db import models


class Subscriber(models.Model):
    """Newsletter sign-up with double opt-in (confirm) and one-click unsubscribe."""

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False, help_text="Подтверждён по e-mail")
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        ordering = ["-subscribed_at"]
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики рассылки"

    def __str__(self):
        return self.email
