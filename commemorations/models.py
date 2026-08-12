"""Записки о поминовении — подача с сайта и печать списка для алтаря.

Устройство отличается от донорского (там два отдельных класса —
разовая записка и сорокоуст). Здесь одна модель с полем `kind` и
счётчиком литургий: разовая записка — это счётчик на 1, сорокоуст —
на 40. Секретарь видит один список вместо двух, а печать проходит
одним и тем же путём.
"""

from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .storage import batch_storage


def split_names(value):
    """Записка — это список имён, по одному в строке."""
    return [line.strip() for line in (value or "").splitlines() if line.strip()]


class CommemorationBatch(models.Model):
    """Пачка записок, собранная к одной службе и выведенная в один PDF."""

    class Status(models.TextChoices):
        CREATED = "created", _("Собрана")
        PDF_READY = "pdf_ready", _("PDF готов")
        PRINTED = "printed", _("Напечатана")
        FAILED = "failed", _("Ошибка")

    title = models.CharField(_("Название"), max_length=200, blank=True)
    service_date = models.DateField(_("К службе"), blank=True, null=True)
    pdf_file = models.FileField(
        _("PDF"),
        upload_to="commemorations/batches/",
        storage=batch_storage,
        blank=True,
    )
    status = models.CharField(
        _("Состояние"), max_length=20, choices=Status.choices, default=Status.CREATED
    )
    error_message = models.TextField(_("Ошибка"), blank=True)
    created_at = models.DateTimeField(_("Собрана"), auto_now_add=True)
    printed_at = models.DateTimeField(_("Напечатана"), blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("пачка записок")
        verbose_name_plural = _("пачки записок")

    def __str__(self):
        if self.title:
            return self.title
        if self.service_date:
            return f"Записки к {self.service_date:%d.%m.%Y}"
        return f"Пачка записок №{self.pk or '—'}"

    @property
    def note_count(self):
        return self.notes.count()


class Commemoration(models.Model):
    """Одна записка: кто подал, кого поминать о здравии и о упокоении."""

    SOROKOUST_LITURGIES = 40

    class Kind(models.TextChoices):
        LITURGY = "liturgy", _("Обедня — на ближайшей литургии")
        SOROKOUST = "sorokoust", _("Сорокоуст — 40 литургий")

    class Status(models.TextChoices):
        PENDING = "pending", _("Ждёт литургии")
        BATCHED = "batched", _("В пачке")
        COMPLETED = "completed", _("Вычитана")

    kind = models.CharField(
        _("Вид поминовения"), max_length=20, choices=Kind.choices, default=Kind.LITURGY
    )
    requester_name = models.CharField(_("Кто подаёт"), max_length=200, blank=True)
    email = models.EmailField(_("E-mail"), blank=True)
    phone = models.CharField(_("Телефон"), max_length=30, blank=True)

    living_names = models.TextField(_("О здравии"), blank=True)
    departed_names = models.TextField(_("О упокоении"), blank=True)
    notes = models.TextField(_("Примечание для священника"), blank=True)

    status = models.CharField(
        _("Состояние"), max_length=20, choices=Status.choices, default=Status.PENDING
    )
    # Связь «многие ко многим», а не ссылка на одну пачку: сорокоуст
    # попадает в сорок разных пачек, и каждая из них должна остаться
    # воспроизводимой — по ней потом пересобирают тот же лист.
    batches = models.ManyToManyField(
        CommemorationBatch,
        verbose_name=_("Пачки"),
        blank=True,
        related_name="notes",
    )

    # Разовая записка — 1 литургия, сорокоуст — 40. Одна механика на оба вида.
    first_service_date = models.DateField(_("Первая литургия"), blank=True, null=True)
    total_liturgies = models.PositiveSmallIntegerField(_("Всего литургий"), default=1)
    printed_count = models.PositiveSmallIntegerField(_("Напечатано раз"), default=0)

    submitted_at = models.DateTimeField(_("Подана"), auto_now_add=True)
    batched_at = models.DateTimeField(_("Взята в пачку"), blank=True, null=True)
    printed_at = models.DateTimeField(_("Напечатана"), blank=True, null=True)
    completed_at = models.DateTimeField(_("Вычитана"), blank=True, null=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = _("записка")
        verbose_name_plural = _("записки")
        indexes = [models.Index(fields=["status", "kind"])]

    def __str__(self):
        who = self.requester_name or self.email or f"№{self.pk or '—'}"
        return f"{who} — {self.get_kind_display()}"

    def save(self, *args, **kwargs):
        if self.kind == self.Kind.SOROKOUST:
            if self.total_liturgies < self.SOROKOUST_LITURGIES:
                self.total_liturgies = self.SOROKOUST_LITURGIES
        elif not self.pk:
            self.total_liturgies = 1
        super().save(*args, **kwargs)

    @property
    def living_list(self):
        return split_names(self.living_names)

    @property
    def departed_list(self):
        return split_names(self.departed_names)

    @property
    def name_count(self):
        return len(self.living_list) + len(self.departed_list)

    @property
    def remaining_liturgies(self):
        return max(self.total_liturgies - self.printed_count, 0)

    @property
    def is_active(self):
        """Записку ещё нужно печатать при следующем сборе пачки."""
        return self.completed_at is None and self.remaining_liturgies > 0

    @property
    def last_service_date(self):
        """Сорокоуст читается 40 литургий; при обычном приходском круге
        это примерно 39 недель от первой — дата ориентировочная и нужна
        только чтобы человек понимал срок."""
        if not self.first_service_date or self.total_liturgies <= 1:
            return None
        return self.first_service_date + timedelta(weeks=self.total_liturgies - 1)

    def mark_printed(self):
        """Учесть одну вычитанную литургию.

        Сорокоуст с остатком возвращается в очередь — секретарь увидит его
        в том же списке «ждёт литургии», что и свежие записки, и возьмёт в
        следующую пачку вместе с ними.
        """
        now = timezone.now()
        self.printed_count = min(self.printed_count + 1, self.total_liturgies)
        self.printed_at = now
        if self.remaining_liturgies == 0:
            self.status = self.Status.COMPLETED
            self.completed_at = now
        else:
            self.status = self.Status.PENDING
        self.save(
            update_fields=["printed_count", "printed_at", "status", "completed_at"]
        )
