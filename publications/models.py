from django.db import models
from django.utils.translation import gettext_lazy as _


class Publication(models.Model):
    """A monthly liturgical calendar or a weekly bulletin, uploaded as a PDF."""

    class Kind(models.TextChoices):
        CALENDAR = "calendar", _("Календарь")
        BULLETIN = "bulletin", _("Бюллетень")

    kind = models.CharField(max_length=20, choices=Kind.choices)
    title = models.CharField(max_length=200)
    period_label = models.CharField(
        "Период", max_length=100, help_text="Например «Август 2026» или «Неделя 17–23 августа»"
    )
    pdf_file = models.FileField(upload_to="publications/%Y/")
    published_at = models.DateField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Публикация"
        verbose_name_plural = "Календарь и бюллетень"

    def __str__(self):
        return f"{self.get_kind_display()}: {self.title}"
