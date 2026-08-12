"""Parish council portal.

Two tiers of access, granted by Django group membership and driven by a single
source of truth — the user's MembershipRequest status:

  Совет прихода (GROUP_COUNCIL)   — sees everything, including council-only
                                    protocols and financial reports;
  Прихожанин   (GROUP_PARISHIONER) — sees what the council chose to share.

A signed-in user in neither group has registered but not yet been approved.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .storage import council_storage

User = settings.AUTH_USER_MODEL

GROUP_COUNCIL = "Совет прихода"
GROUP_PARISHIONER = "Прихожанин"


def sync_portal_groups(membership_request):
    """Make the user's portal groups match their request status.

    Status is the single source of truth: an approved request puts the user in
    Council (when is_council_member) or Parishioner; anything else removes both.
    Safe to call repeatedly — the admin, a bulk action and the shell all go
    through here rather than each poking at groups themselves.
    """
    from django.contrib.auth.models import Group

    user = membership_request.user
    council, _created = Group.objects.get_or_create(name=GROUP_COUNCIL)
    parish, _created = Group.objects.get_or_create(name=GROUP_PARISHIONER)

    if membership_request.status == MembershipRequest.Status.APPROVED:
        if membership_request.is_council_member:
            user.groups.add(council)
            user.groups.remove(parish)
        else:
            user.groups.add(parish)
            user.groups.remove(council)
    else:
        user.groups.remove(council, parish)


class MembershipRequest(models.Model):
    """A parishioner's request for access to the portal.

    The account is created at registration; access is granted only once the
    rector or an administrator approves the request.
    """

    class Status(models.TextChoices):
        PENDING = "pending", _("На рассмотрении")
        APPROVED = "approved", _("Одобрено")
        REJECTED = "rejected", _("Отклонено")

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="membership_request")
    phone = models.CharField("Телефон", max_length=30, blank=True)
    parish_connection = models.CharField(
        "Связь с приходом", max_length=200, blank=True,
        help_text="Как человек связан с приходом — необязательно.",
    )
    note = models.TextField("Сообщение", blank=True, help_text="Что заявитель хочет сообщить совету.")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    is_council_member = models.BooleanField(
        "Член совета", default=False,
        help_text="Отметьте до одобрения, чтобы дать полный доступ — "
                  "протоколы для совета и финансовые отчёты.",
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="approved_membership_requests",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка на доступ"
        verbose_name_plural = "Заявки на доступ"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} — {self.get_status_display()}"


class Meeting(models.Model):
    """A parish council meeting."""

    class Status(models.TextChoices):
        PLANNED = "planned", _("Запланировано")
        HELD = "held", _("Состоялось")
        CANCELLED = "cancelled", _("Отменено")

    title = models.CharField("Название", max_length=300)
    date = models.DateField("Дата")
    time = models.TimeField("Время", null=True, blank=True)
    location = models.CharField("Место", max_length=300, blank=True)
    agenda = models.TextField("Повестка", blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PLANNED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-time"]
        verbose_name = "Заседание совета"
        verbose_name_plural = "Заседания совета"

    def __str__(self):
        return f"{self.title} — {self.date:%d.%m.%Y}"

    @property
    def is_upcoming(self):
        return self.status == self.Status.PLANNED and self.date >= timezone.now().date()


class Protocol(models.Model):
    """Minutes of a meeting."""

    meeting = models.ForeignKey(
        Meeting, on_delete=models.CASCADE, related_name="protocols", null=True, blank=True,
    )
    title = models.CharField("Название", max_length=300)
    body = models.TextField("Протокол", blank=True)
    decisions = models.TextField(
        "Решения", blank=True,
        help_text="Что решили, кто отвечает, к какому сроку.",
    )
    file = models.FileField(
        "Файл", upload_to="council/protocols/", blank=True, null=True, storage=council_storage,
        help_text="Необязательно: приложенный документ (PDF / DOCX).",
    )
    council_only = models.BooleanField(
        "Только для совета", default=True,
        help_text="Выключите, чтобы протокол увидели все одобренные прихожане.",
    )
    is_published = models.BooleanField(
        "Опубликован", default=True, help_text="Черновики в портале не видны.",
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_protocols",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Протокол"
        verbose_name_plural = "Протоколы"

    def __str__(self):
        return self.title


class Report(models.Model):
    """A financial or activity report shared in the portal."""

    class Category(models.TextChoices):
        FINANCIAL = "financial", _("Финансовый")
        ACTIVITY = "activity", _("О деятельности")
        OTHER = "other", _("Другое")

    title = models.CharField("Название", max_length=300)
    category = models.CharField(max_length=12, choices=Category.choices, default=Category.FINANCIAL)
    period = models.CharField(
        "Период", max_length=100, blank=True, help_text="Например «I квартал 2026» или «2025 год».",
    )
    body = models.TextField("Кратко", blank=True)
    file = models.FileField(
        "Файл", upload_to="council/reports/", blank=True, null=True, storage=council_storage,
        help_text="Приложенный отчёт (PDF / XLSX) — доступен одобренным участникам.",
    )
    council_only = models.BooleanField(
        "Только для совета", default=True,
        help_text="Выключите, чтобы отчёт увидели все одобренные прихожане.",
    )
    is_published = models.BooleanField("Опубликован", default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_council_reports",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Отчёт совета"
        verbose_name_plural = "Отчёты совета"

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class MeetingDocument(models.Model):
    """Any file attached to a meeting: audio, reports, photos, presentations."""

    class Category(models.TextChoices):
        FINANCIAL = "financial", _("Финансовый отчёт")
        COMMITTEE = "committee", _("Отчёт комиссии")
        AUDIO = "audio", _("Аудиозапись")
        PHOTO = "photo", _("Фото")
        PRESENTATION = "presentation", _("Презентация")
        OTHER = "other", _("Другой документ")

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField("Название", max_length=300)
    category = models.CharField(max_length=12, choices=Category.choices, default=Category.OTHER)
    file = models.FileField("Файл", upload_to="council/meeting_docs/%Y/%m/", storage=council_storage)
    description = models.TextField("Описание", blank=True)
    council_only = models.BooleanField(
        "Только для совета", default=True,
        help_text="Выключите, чтобы файл увидели все одобренные прихожане.",
    )
    is_published = models.BooleanField("Опубликован", default=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="uploaded_meeting_docs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "title"]
        verbose_name = "Документ заседания"
        verbose_name_plural = "Документы заседаний"

    def __str__(self):
        return self.title

    @property
    def is_image(self):
        return (self.file.name or "").lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))

    @property
    def is_audio(self):
        return (self.file.name or "").lower().endswith((".mp3", ".m4a", ".ogg", ".wav"))


class ActionItem(models.Model):
    """A task or decision with an owner and a due date.

    Deliberately shared between the council and the ministries: a decision taken
    at a meeting is usually carried out inside a ministry, and splitting that
    into two unrelated task lists is how things get lost.
    """

    class Status(models.TextChoices):
        OPEN = "open", _("В работе")
        DONE = "done", _("Выполнено")

    title = models.CharField("Задача", max_length=300)
    description = models.TextField("Описание", blank=True)
    meeting = models.ForeignKey(
        Meeting, on_delete=models.SET_NULL, null=True, blank=True, related_name="action_items",
    )
    protocol = models.ForeignKey(
        Protocol, on_delete=models.SET_NULL, null=True, blank=True, related_name="action_items",
    )
    ministry = models.ForeignKey(
        "ministries.Ministry", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="action_items",
    )
    ministry_project = models.ForeignKey(
        "ministries.MinistryProject", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="action_items",
    )
    assignee = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="action_items",
    )
    due_date = models.DateField("Срок", null=True, blank=True)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["status", "due_date", "-created_at"]
        verbose_name = "Поручение"
        verbose_name_plural = "Поручения"

    def __str__(self):
        return self.title

    # Порог «скоро»: неделя. Совет собирается раз в месяц, но поручения
    # исполняются между заседаниями, и неделя — это горизонт, на который
    # человек реально планирует ближайшие дела.
    DUE_SOON_DAYS = 7

    @property
    def days_left(self):
        """Дней до срока; отрицательное — просрочено. None, если срока нет."""
        if self.due_date is None:
            return None
        return (self.due_date - timezone.now().date()).days

    @property
    def is_overdue(self):
        left = self.days_left
        return self.status == self.Status.OPEN and left is not None and left < 0

    @property
    def is_due_soon(self):
        left = self.days_left
        return (
            self.status == self.Status.OPEN
            and left is not None
            and 0 <= left <= self.DUE_SOON_DAYS
        )


class CouncilProject(models.Model):
    """A project of the parish council itself, not of a single ministry."""

    class Status(models.TextChoices):
        IDEA = "idea", _("Идея")
        PLANNED = "planned", _("Запланирован")
        IN_PROGRESS = "in_progress", _("В работе")
        DONE = "done", _("Завершён")

    title = models.CharField("Название", max_length=300)
    description = models.TextField("Описание", blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PLANNED)
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="council_projects",
    )
    due_date = models.DateField("Срок", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["status", "due_date", "-created_at"]
        verbose_name = "Проект совета"
        verbose_name_plural = "Проекты совета"

    def __str__(self):
        return self.title


class GroupMailing(models.Model):
    """An email sent to a parish group — kept as an audit log of what went out,
    to whom, and from whom."""

    class Audience(models.TextChoices):
        COUNCIL = "council", _("Совет прихода")
        PARISHIONERS = "parishioners", _("Все одобренные прихожане")
        MINISTRY = "ministry", _("Одно служение")

    audience = models.CharField("Кому", max_length=14, choices=Audience.choices)
    ministry = models.ForeignKey(
        "ministries.Ministry", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="mailings",
    )
    subject = models.CharField("Тема", max_length=300)
    body = models.TextField("Текст")
    sent_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sent_mailings",
    )
    recipient_count = models.PositiveIntegerField("Получателей", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"{self.subject} ({self.created_at:%d.%m.%Y})"

    @property
    def audience_label(self):
        if self.audience == self.Audience.MINISTRY and self.ministry:
            return self.ministry.name
        return self.get_audience_display()


class GroupMailingAttachment(models.Model):
    mailing = models.ForeignKey(GroupMailing, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="council/mailings/%Y/%m/", storage=council_storage)
    original_name = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Вложение рассылки"
        verbose_name_plural = "Вложения рассылок"

    def __str__(self):
        return self.original_name or self.file.name
