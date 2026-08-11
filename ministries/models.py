from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .storage import private_storage

User = settings.AUTH_USER_MODEL


class Ministry(models.Model):
    """A parish ministry — public card + a member/leader portal workspace."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, allow_unicode=True)
    image = models.ImageField(upload_to="ministries/", blank=True)
    description = models.TextField(blank=True)
    announcement = models.TextField(blank=True, help_text="Короткая закреплённая новость на странице служения")
    leaders = models.ManyToManyField(User, related_name="led_ministries", blank=True)
    is_private = models.BooleanField(
        default=False, help_text="Закрытое служение: содержимое видно только участникам и лидерам"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Служение"
        verbose_name_plural = "Служения"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name, allow_unicode=True) or "ministry"
            slug = base
            i = 2
            while Ministry.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def is_leader(self, user):
        if not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff:
            return True
        if self.leaders.filter(pk=user.pk).exists():
            return True
        return self.memberships.filter(user=user, role=MinistryMembership.Role.LEADER,
                                        status=MinistryMembership.Status.ACTIVE).exists()

    def is_member(self, user):
        if self.is_leader(user):
            return True
        if not user.is_authenticated:
            return False
        return self.memberships.filter(user=user, status=MinistryMembership.Status.ACTIVE).exists()

    def membership_for(self, user):
        if not user.is_authenticated:
            return None
        return self.memberships.filter(user=user).first()


class MinistryMembership(models.Model):
    class Role(models.TextChoices):
        MEMBER = "member", _("Участник")
        LEADER = "leader", _("Лидер")

    class Status(models.TextChoices):
        PENDING = "pending", _("Заявка на рассмотрении")
        ACTIVE = "active", _("Активен")

    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ministry_memberships")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    message = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_memberships"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("ministry", "user")
        verbose_name = "Участие в служении"
        verbose_name_plural = "Участие в служениях"

    def __str__(self):
        return f"{self.user} — {self.ministry} ({self.get_role_display()})"


VISIBILITY_CHOICES = [
    ("all", _("Все посетители портала")),
    ("members", _("Только участники служения")),
    ("leaders", _("Только лидеры служения")),
]


class MinistryProject(models.Model):
    class Status(models.TextChoices):
        IDEA = "idea", _("Идея")
        PLANNED = "planned", _("Запланирован")
        IN_PROGRESS = "in_progress", _("В работе")
        DONE = "done", _("Завершён")

    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IDEA)
    due_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Проект служения"
        verbose_name_plural = "Проекты служений"

    def __str__(self):
        return self.title


class MinistryTopic(models.Model):
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name="topics")
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]
        verbose_name = "Тема обсуждения"
        verbose_name_plural = "Темы обсуждений"

    def __str__(self):
        return self.title


class MinistryComment(models.Model):
    topic = models.ForeignKey(MinistryTopic, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"Комментарий к «{self.topic}»"


def ministry_attachment_path(instance, filename):
    return f"ministries/{instance.topic.ministry_id if instance.topic else 'x'}/attachments/{filename}"


class MinistryAttachment(models.Model):
    topic = models.ForeignKey(MinistryTopic, on_delete=models.CASCADE, null=True, blank=True, related_name="attachments")
    comment = models.ForeignKey(MinistryComment, on_delete=models.CASCADE, null=True, blank=True, related_name="attachments")
    file = models.FileField(upload_to=ministry_attachment_path, storage=private_storage)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Вложение"
        verbose_name_plural = "Вложения"

    def __str__(self):
        return self.file.name

    @property
    def is_image(self):
        return self.file.name.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))


class MinistryDocument(models.Model):
    class Category(models.TextChoices):
        GENERAL = "general", _("Общее")
        FINANCIAL = "financial", _("Финансы")
        PLAN = "plan", _("План/протокол")
        PHOTO = "photo", _("Фото")
        OTHER = "other", _("Другое")

    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="ministries/%Y/documents/", storage=private_storage)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="members")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Документ служения"
        verbose_name_plural = "Документы служений"

    def __str__(self):
        return self.title


class MinistryReport(models.Model):
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name="reports")
    title = models.CharField(max_length=200)
    period = models.CharField(max_length=100, blank=True)
    body = models.TextField(blank=True)
    file = models.FileField(upload_to="ministries/%Y/reports/", storage=private_storage, blank=True)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default="all")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Отчёт служения"
        verbose_name_plural = "Отчёты служений"

    def __str__(self):
        return self.title


class MinistryPhoto(models.Model):
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="ministries/%Y/photos/")
    caption = models.CharField(max_length=200, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Фото служения"
        verbose_name_plural = "Фото служений"

    def __str__(self):
        return self.caption or f"Фото #{self.pk}"


class MinistryScheduleEntry(models.Model):
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name="schedule_entries")
    date = models.DateField()
    person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ministry_shifts")
    second_person = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ministry_shifts_second"
    )
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["date"]
        verbose_name = "Запись в графике"
        verbose_name_plural = "График служений"

    def __str__(self):
        return f"{self.ministry} — {self.date:%d.%m.%Y}"


class MinistrySupplyRequest(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", _("Нужно купить")
        DONE = "done", _("Куплено")

    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, related_name="supply_requests")
    item = models.CharField(max_length=200)
    note = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["status", "-created_at"]
        verbose_name = "Заявка на закупку"
        verbose_name_plural = "Заявки на закупку"

    def __str__(self):
        return self.item
