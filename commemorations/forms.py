import re
import time

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Commemoration

# Форму заполняет живой человек, значит она не может быть отправлена
# мгновенно. Порог намеренно низкий — он отсекает ботов, а не пожилого
# прихожанина, который печатает медленно.
MIN_SUBMIT_SECONDS = 3
MAX_NAMES_PER_LIST = 80
MAX_NAME_LENGTH = 80

# Подсказка в поле показывает ровно ту форму, которую просит help_text:
# родительный падеж и церковное написание имени. В английской версии
# нужны английские образцы, поэтому строка переводимая.
NAMES_PLACEHOLDER = _("Марии\nИоанна\nмл. Анны")


def normalize_name_lines(value):
    """Люди перечисляют имена и через запятую, и через точку с запятой,
    и в столбик. Приводим к одному имени на строку."""
    pieces = re.split(r"[\n,;]+", value or "")
    return "\n".join(piece.strip() for piece in pieces if piece.strip())


class CommemorationForm(forms.ModelForm):
    # Ловушка для ботов: поле спрятано и от глаза, и от табуляции, так что
    # заполнить его может только автомат, читающий разметку.
    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "autocomplete": "off",
            "tabindex": "-1",
            "aria-hidden": "true",
            "class": "honeypot",
        }),
    )
    form_timestamp = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Commemoration
        fields = [
            "kind", "requester_name", "email", "phone",
            "living_names", "departed_names", "notes",
        ]
        labels = {
            "kind": _("Вид поминовения"),
            "requester_name": _("Ваше имя"),
            "email": _("E-mail"),
            "phone": _("Телефон"),
            "living_names": _("О здравии"),
            "departed_names": _("О упокоении"),
            "notes": _("Примечание для священника"),
        }
        help_texts = {
            "living_names": _("По одному имени в строке, в родительном падеже "
                              "и в церковной форме: Марии, Иоанна, Александра."),
            "departed_names": _("По одному имени в строке. Отмечайте, если нужно: "
                                "мл. — младенца, отр. — отрока, прот. — протоиерея."),
        }
        widgets = {
            "living_names": forms.Textarea(attrs={"rows": 8, "placeholder": NAMES_PLACEHOLDER}),
            "departed_names": forms.Textarea(attrs={"rows": 8, "placeholder": NAMES_PLACEHOLDER}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kind"].choices = Commemoration.Kind.choices
        self.fields["kind"].widget = forms.RadioSelect(
            attrs={"class": "radio-group"}, choices=Commemoration.Kind.choices
        )
        self.fields["kind"].initial = Commemoration.Kind.LITURGY

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError(_("Не удалось принять записку."))
        return ""

    def clean_form_timestamp(self):
        raw = self.cleaned_data.get("form_timestamp", "")
        try:
            elapsed = time.time() - float(raw)
        except (TypeError, ValueError):
            raise forms.ValidationError(_("Не удалось принять записку."))
        if elapsed < MIN_SUBMIT_SECONDS:
            raise forms.ValidationError(_("Не удалось принять записку."))
        return raw

    def _clean_names(self, field):
        names = normalize_name_lines(self.cleaned_data.get(field, ""))
        name_list = names.splitlines() if names else []
        if len(name_list) > MAX_NAMES_PER_LIST:
            raise forms.ValidationError(
                _("Не больше %(limit)d имён в одном списке. Разделите записку на несколько.")
                % {"limit": MAX_NAMES_PER_LIST}
            )
        if any(len(name) > MAX_NAME_LENGTH for name in name_list):
            raise forms.ValidationError(
                _("Каждое имя — короче %(limit)d знаков. Похоже, в строку попало что-то лишнее.")
                % {"limit": MAX_NAME_LENGTH}
            )
        return names

    def clean_living_names(self):
        return self._clean_names("living_names")

    def clean_departed_names(self):
        return self._clean_names("departed_names")

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("living_names") and not cleaned.get("departed_names"):
            raise forms.ValidationError(
                _("Впишите хотя бы одно имя — о здравии или о упокоении.")
            )
        if not cleaned.get("email") and not cleaned.get("phone"):
            raise forms.ValidationError(
                _("Оставьте e-mail или телефон — на случай если нужно будет уточнить имена.")
            )
        return cleaned
