from django import forms

from .access import targetable_ministries
from .models import ActionItem, GroupMailing, Meeting, MembershipRequest, Protocol, Report


class MembershipRequestForm(forms.ModelForm):
    class Meta:
        model = MembershipRequest
        fields = ["phone", "parish_connection", "note"]
        widgets = {"note": forms.Textarea(attrs={"rows": 4})}


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ["title", "date", "time", "location", "agenda", "status"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
            "agenda": forms.Textarea(attrs={"rows": 6}),
        }


class ProtocolForm(forms.ModelForm):
    class Meta:
        model = Protocol
        fields = ["meeting", "title", "body", "decisions", "file", "council_only", "is_published"]
        widgets = {
            "body": forms.Textarea(attrs={"rows": 10}),
            "decisions": forms.Textarea(attrs={"rows": 5}),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["title", "category", "period", "body", "file", "council_only", "is_published"]
        widgets = {"body": forms.Textarea(attrs={"rows": 6})}


class ActionItemForm(forms.ModelForm):
    class Meta:
        model = ActionItem
        fields = ["title", "description", "assignee", "due_date", "meeting", "ministry", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class MultipleFileInput(forms.ClearableFileInput):
    """Django refuses `multiple` on the stock widget; this is the documented
    way to accept several files in one field."""

    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single = super().clean
        if isinstance(data, (list, tuple)):
            return [single(d, initial) for d in data]
        return single(data, initial)


class MailingForm(forms.Form):
    audience = forms.ChoiceField(label="Кому", choices=GroupMailing.Audience.choices)
    ministry = forms.ModelChoiceField(
        label="Служение", queryset=None, required=False,
        help_text="Только если выбрано «Одно служение».",
    )
    subject = forms.CharField(label="Тема", max_length=300)
    body = forms.CharField(label="Текст", widget=forms.Textarea(attrs={"rows": 10}))
    attachments = MultipleFileField(label="Вложения", required=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields["ministry"].queryset = targetable_ministries(user)
        # A ministry leader who is not on the council may only write to their
        # own ministry — so the wider audiences are not offered at all.
        from .access import is_council_member

        if user and not (user.is_superuser or is_council_member(user)):
            self.fields["audience"].choices = [
                (GroupMailing.Audience.MINISTRY, GroupMailing.Audience.MINISTRY.label)
            ]
            self.fields["ministry"].required = True

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("audience") == GroupMailing.Audience.MINISTRY and not cleaned.get("ministry"):
            raise forms.ValidationError("Выберите служение, которому пишете.")
        return cleaned
