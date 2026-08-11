from django.db import models

from core.models import SingletonModel


class RussianSchoolPage(SingletonModel):
    """Structured content for the Russian language school page."""

    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="school/", blank=True)
    age_from = models.PositiveIntegerField(default=5)
    schedule_text = models.CharField(
        max_length=300, blank=True,
        help_text="Например «По понедельникам, 16:00–20:00»",
    )
    term_start = models.DateField(null=True, blank=True)
    term_end = models.DateField(null=True, blank=True)
    tuition_note = models.CharField(max_length=300, blank=True)
    enrollment_open = models.BooleanField(default=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Русская школа"
        verbose_name_plural = "Русская школа"

    def __str__(self):
        return "Русская школа"


class RussianSchoolPhoto(models.Model):
    page = models.ForeignKey(RussianSchoolPage, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="school/photos/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Фото школы"
        verbose_name_plural = "Фото школы"

    def __str__(self):
        return self.caption or f"Фото #{self.pk}"
