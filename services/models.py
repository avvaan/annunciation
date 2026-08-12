import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ServiceType(models.Model):
    """Lookup list of service kinds — Утреня, Часы, Литургия, Всенощное бдение, Акафист…

    A separate table (not free text) so the composition of a service day is picked
    from a controlled list and stays consistent across the whole schedule.
    """

    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Тип службы"
        verbose_name_plural = "Типы служб"

    def __str__(self):
        return self.name


class FastingLevel(models.TextChoices):
    """The six gradations a Russian parish calendar actually marks."""

    NONE = "none", _("Обычный день")
    FAST = "fast", _("Пост")
    FISH_WINE_OIL = "fish_wine_oil", _("Рыба, вино и елей")
    WINE_OIL = "wine_oil", _("Вино и елей")
    DRY = "dry", _("Сухоядение")
    STRICT = "strict", _("Строгий пост")


# Marked for translation: the card shows the weekday, and on /en/ it must read
# "Friday", not "Пятница". Kept lazy so the active language is resolved at render.
WEEKDAY_NAMES = [
    _("Понедельник"), _("Вторник"), _("Среда"), _("Четверг"),
    _("Пятница"), _("Суббота"), _("Воскресенье"),
]

# «В среду», а не «Среда»: относительная подпись читается предложением,
# и предложный падеж здесь не украшение, а грамматика.
WEEKDAY_IN_PREPOSITIONAL = [
    _("В понедельник"), _("Во вторник"), _("В среду"), _("В четверг"),
    _("В пятницу"), _("В субботу"), _("В воскресенье"),
]

# Месяцы в родительном падеже: «12 августа», а не «12 Август». Django-шный
# фильтр date:"j F" уже даёт нужную форму для ru, но заголовок месяца
# («Август 2026») требует именительного — держим оба списка явно.
MONTH_NOMINATIVE = [
    _("Январь"), _("Февраль"), _("Март"), _("Апрель"), _("Май"), _("Июнь"),
    _("Июль"), _("Август"), _("Сентябрь"), _("Октябрь"), _("Ноябрь"), _("Декабрь"),
]

# The Julian/Gregorian gap is 13 days for the whole 20th–21st century and only
# widens to 14 days from 1 March 2100 (new style) onward.
_JULIAN_GAP_CHANGE_DATE = datetime.date(2100, 3, 1)


def gregorian_to_julian_label(date):
    """Return the Julian ("old style") calendar date as a 'D month' Russian string."""
    gap = datetime.timedelta(days=13 if date < _JULIAN_GAP_CHANGE_DATE else 14)
    old_style = date - gap
    return old_style


class RecurringServiceRule(models.Model):
    """
    A weekly template ("every Saturday: Всенощное бдение 18:00; every Sunday: Часы
    9:00, Литургия 9:30") that the secretary can generate a month of ServiceDay
    entries from in one click, then adjust individual days for feasts and fasts.
    """

    WEEKDAY_CHOICES = [
        (0, _("Понедельник")), (1, _("Вторник")), (2, _("Среда")),
        (3, _("Четверг")), (4, _("Пятница")), (5, _("Суббота")), (6, _("Воскресенье")),
    ]

    title = models.CharField(max_length=200, help_text="Для себя, в списке правил — например «Воскресное»")
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAY_CHOICES)
    default_fasting_level = models.CharField(
        max_length=20, choices=FastingLevel.choices, default=FastingLevel.NONE
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["weekday"]
        verbose_name = "Регулярное правило расписания"
        verbose_name_plural = "Регулярные правила расписания"

    def __str__(self):
        return f"{self.title} ({self.get_weekday_display()})"


class RecurringServiceItem(models.Model):
    rule = models.ForeignKey(RecurringServiceRule, on_delete=models.CASCADE, related_name="items")
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    time = models.TimeField()
    note = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "time"]
        verbose_name = "Служба в правиле"
        verbose_name_plural = "Службы в правиле"

    def __str__(self):
        return f"{self.service_type} {self.time:%H:%M}"


class ServiceDay(models.Model):
    """One card on the public schedule page."""

    date = models.DateField(db_index=True)
    feast_title = models.CharField("Праздник/память", max_length=300, blank=True)
    is_major = models.BooleanField(
        "Великий праздник", default=False,
        help_text="Двунадесятый или престольный праздник — название выделяется на карточке.",
    )
    fasting_level = models.CharField(
        max_length=20, choices=FastingLevel.choices, default=FastingLevel.NONE
    )
    note = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    generated_from_rule = models.ForeignKey(
        RecurringServiceRule, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="generated_days",
    )

    class Meta:
        ordering = ["date"]
        unique_together = ("date",)
        verbose_name = "День службы"
        verbose_name_plural = "Расписание богослужений"

    def __str__(self):
        return f"{self.date:%d.%m.%Y} — {self.feast_title or self.get_fasting_level_display()}"

    @property
    def old_style_date(self):
        return gregorian_to_julian_label(self.date)

    @property
    def weekday(self):
        return self.date.weekday()

    @property
    def weekday_label(self):
        return WEEKDAY_NAMES[self.date.weekday()]

    # ------------------------------------------------------------------
    # Ориентация во времени. Прихожанин спрашивает «а завтра служба есть?»,
    # а не «что стоит в клетке 16.08.2026». Раньше он должен был сначала
    # вспомнить сегодняшнее число и вычесть его в уме.
    # ------------------------------------------------------------------

    @property
    def days_away(self):
        return (self.date - timezone.localdate()).days

    @property
    def is_today(self):
        return self.days_away == 0

    @property
    def is_tomorrow(self):
        return self.days_away == 1

    @property
    def relative_label(self):
        """«Сегодня», «Завтра», «В воскресенье» — или ничего, если далеко.

        Дальше недели относительная подпись перестаёт помогать: «через
        девятнадцать дней» человек всё равно переводит обратно в дату.
        """
        days = self.days_away
        if days == 0:
            return _("Сегодня")
        if days == 1:
            return _("Завтра")
        if 2 <= days <= 6:
            return WEEKDAY_IN_PREPOSITIONAL[self.date.weekday()]
        return ""

    # Шесть градаций поста — это шкала, а не список: сухоядение и «рыба,
    # вино и елей» противоположны по смыслу, и одинаковая метка на них
    # вводила в заблуждение. Три ступени видимости — столько и различает
    # глаз при беглом взгляде.
    FASTING_TIERS = {
        FastingLevel.STRICT: "strict",
        FastingLevel.DRY: "strict",
        FastingLevel.FAST: "fast",
        FastingLevel.WINE_OIL: "fast",
        FastingLevel.FISH_WINE_OIL: "light",
    }

    @property
    def fasting_tier(self):
        return self.FASTING_TIERS.get(self.fasting_level, "")

    @property
    def has_services(self):
        return self.items.exists()


class ServiceItem(models.Model):
    day = models.ForeignKey(ServiceDay, on_delete=models.CASCADE, related_name="items")
    service_type = models.ForeignKey(ServiceType, on_delete=models.PROTECT)
    time = models.TimeField()
    note = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "time"]
        verbose_name = "Служба"
        verbose_name_plural = "Службы"

    def __str__(self):
        return f"{self.service_type} {self.time:%H:%M}"
