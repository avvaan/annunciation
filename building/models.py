from django.db import models

from core.models import SingletonModel


class BuildingProject(SingletonModel):
    """The parish's current construction/renovation campaign, shown as a progress page."""

    title = models.CharField(max_length=200, default="Строительство нового храма")
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="building/", blank=True)
    goal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    raised_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Обновляется вручную по данным Realm/казначея — прямой синхронизации нет.",
    )
    raised_updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Строительный проект"
        verbose_name_plural = "Строительный проект"

    def __str__(self):
        return self.title

    @property
    def percent_raised(self):
        if not self.goal_amount:
            return 0
        return min(100, round(self.raised_amount / self.goal_amount * 100))


class BuildingProjectUpdate(models.Model):
    project = models.ForeignKey(BuildingProject, on_delete=models.CASCADE, related_name="updates")
    date = models.DateField()
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="building/updates/", blank=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Новость стройки"
        verbose_name_plural = "Новости стройки"

    def __str__(self):
        return f"{self.date:%d.%m.%Y} — {self.title}"


class BuildingProjectPhoto(models.Model):
    project = models.ForeignKey(BuildingProject, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="building/photos/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Фото стройки"
        verbose_name_plural = "Фото стройки"

    def __str__(self):
        return self.caption or f"Фото #{self.pk}"
