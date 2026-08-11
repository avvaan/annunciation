from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Subscriber


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["email", "name"]
        labels = {"email": _("E-mail"), "name": _("Имя")}
