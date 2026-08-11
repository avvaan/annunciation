from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    MinistryComment,
    MinistryMembership,
    MinistryPhoto,
    MinistryScheduleEntry,
    MinistrySupplyRequest,
    MinistryTopic,
)


class SignupForm(UserCreationForm):
    email = forms.EmailField(label="E-mail", required=True)
    first_name = forms.CharField(label="Имя", required=True)
    last_name = forms.CharField(label="Фамилия", required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Повторите пароль"


class MinistryJoinForm(forms.ModelForm):
    class Meta:
        model = MinistryMembership
        fields = ["message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 3, "placeholder": "Коротко о себе (необязательно)"})}
        labels = {"message": "Сообщение лидеру"}


class MinistryTopicForm(forms.ModelForm):
    class Meta:
        model = MinistryTopic
        fields = ["title", "body"]
        labels = {"title": "Заголовок темы", "body": "Текст"}


class MinistryCommentForm(forms.ModelForm):
    class Meta:
        model = MinistryComment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}
        labels = {"body": "Ваш ответ"}


class MinistryPhotoForm(forms.ModelForm):
    class Meta:
        model = MinistryPhoto
        fields = ["image", "caption"]
        labels = {"image": "Фотография", "caption": "Подпись"}


class MinistrySupplyRequestForm(forms.ModelForm):
    class Meta:
        model = MinistrySupplyRequest
        fields = ["item", "note"]
        labels = {"item": "Что нужно купить", "note": "Комментарий"}


class MinistryScheduleEntryForm(forms.ModelForm):
    class Meta:
        model = MinistryScheduleEntry
        fields = ["date", "person", "second_person", "note"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
        labels = {
            "date": "Дата", "person": "Ответственный",
            "second_person": "Второй ответственный", "note": "Комментарий",
        }
