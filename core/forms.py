from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 5})}
        labels = {"name": "Имя", "email": "E-mail", "phone": "Телефон", "message": "Сообщение"}
