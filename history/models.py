from django.db import models


class HistoryMilestone(models.Model):
    """One entry on the parish-history timeline (founding, first church, current building…).

    The long-form introduction text lives in core.PageText via the {% editable %}
    tag directly in the template — no separate model needed for that part.
    """

    year = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="history/", blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "year"]
        verbose_name = "Веха истории"
        verbose_name_plural = "История прихода"

    def __str__(self):
        return f"{self.year} — {self.title}"
