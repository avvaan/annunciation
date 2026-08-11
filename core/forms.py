from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactMessage, Inquiry


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}
        labels = {"name": _("Имя"), "email": _("E-mail"),
                  "phone": _("Телефон"), "message": _("Сообщение")}


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ["name", "about", "email", "phone", "preferred_contact", "best_time", "message"]
        widgets = {
            "about": forms.RadioSelect(attrs={"class": "radio-group"}),
            "message": forms.Textarea(attrs={"rows": 4}),
            "best_time": forms.TextInput(attrs={"placeholder": _("Например, будни после 18:00")}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # a ModelForm choice field ships a blank "---------" option; on a radio
        # group that renders as a nameless fourth button nobody can interpret
        self.fields["about"].choices = Inquiry.About.choices
        self.fields["about"].initial = Inquiry.About.ORTHODOX

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("email") and not cleaned.get("phone"):
            raise forms.ValidationError(
                _("Оставьте e-mail или телефон — иначе мы не сможем вам ответить.")
            )
        return cleaned
