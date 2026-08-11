from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import (
    MinistryComment,
    MinistryMembership,
    MinistryPhoto,
    MinistryScheduleEntry,
    MinistrySupplyRequest,
    MinistryTopic,
)


class SignupForm(UserCreationForm):
    email = forms.EmailField(label=_("E-mail"), required=True)
    first_name = forms.CharField(label=_("Имя"), required=True)
    last_name = forms.CharField(label=_("Фамилия"), required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = _("Логин")
        self.fields["password1"].label = _("Пароль")
        self.fields["password2"].label = _("Повторите пароль")


class MinistryJoinForm(forms.ModelForm):
    class Meta:
        model = MinistryMembership
        fields = ["message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 3, "placeholder": _("Коротко о себе (необязательно)")})}
        labels = {"message": _("Сообщение лидеру")}


class MinistryTopicForm(forms.ModelForm):
    class Meta:
        model = MinistryTopic
        fields = ["title", "body"]
        labels = {"title": _("Заголовок темы"), "body": _("Текст")}


class MinistryCommentForm(forms.ModelForm):
    class Meta:
        model = MinistryComment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}
        labels = {"body": _("Ваш ответ")}


class MinistryPhotoForm(forms.ModelForm):
    class Meta:
        model = MinistryPhoto
        fields = ["image", "caption"]
        labels = {"image": _("Фотография"), "caption": _("Подпись")}


class MinistrySupplyRequestForm(forms.ModelForm):
    class Meta:
        model = MinistrySupplyRequest
        fields = ["item", "note"]
        labels = {"item": _("Что нужно купить"), "note": _("Комментарий")}


class MinistryScheduleEntryForm(forms.ModelForm):
    class Meta:
        model = MinistryScheduleEntry
        fields = ["date", "person", "second_person", "note"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
        labels = {
            "date": _("Дата"), "person": _("Ответственный"),
            "second_person": _("Второй ответственный"), "note": _("Комментарий"),
        }
