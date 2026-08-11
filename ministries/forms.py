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
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label="Имя", required=True)
    last_name = forms.CharField(label="Фамилия", required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username", "password1", "password2"]


class MinistryJoinForm(forms.ModelForm):
    class Meta:
        model = MinistryMembership
        fields = ["message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 3, "placeholder": "Коротко о себе (необязательно)"})}


class MinistryTopicForm(forms.ModelForm):
    class Meta:
        model = MinistryTopic
        fields = ["title", "body"]


class MinistryCommentForm(forms.ModelForm):
    class Meta:
        model = MinistryComment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}


class MinistryPhotoForm(forms.ModelForm):
    class Meta:
        model = MinistryPhoto
        fields = ["image", "caption"]


class MinistrySupplyRequestForm(forms.ModelForm):
    class Meta:
        model = MinistrySupplyRequest
        fields = ["item", "note"]


class MinistryScheduleEntryForm(forms.ModelForm):
    class Meta:
        model = MinistryScheduleEntry
        fields = ["date", "person", "second_person", "note"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
