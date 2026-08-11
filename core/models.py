from django.db import models
from django.utils.translation import gettext_lazy as _


class SingletonModel(models.Model):
    """Base for models that must have exactly one row (site-wide settings, etc.)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        # not `obj, _ = ...` — that would shadow the gettext alias imported above
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    """Parish-wide contact details and external-service links, edited from one admin screen."""

    parish_name = models.CharField(max_length=200, default="Приход Благовещения Пресвятой Богородицы")
    city = models.CharField(max_length=120, default="Джексонвиль, Флорида")
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    # Full-bleed photograph behind the homepage headline. Horizontal, at least
    # 2000px wide — it is cropped to the viewport. Until one is uploaded the
    # hero falls back to a ruled dark ground so the composition still holds.
    hero_image = models.ImageField("Фото на главной", upload_to="hero/", blank=True)
    hero_lede = models.CharField(
        "Подпись на главной", max_length=300, blank=True,
        help_text="Одна-две строки под названием прихода на первом экране.",
    )

    # External membership/giving system (Realm) — no data sync, just outbound links.
    realm_giving_url = models.URLField(
        "Ссылка на пожертвования (Realm)", blank=True,
        help_text="Кнопка «Пожертвовать» ведёт сюда.",
    )
    realm_membership_url = models.URLField(
        "Ссылка на членство (Realm)", blank=True,
        help_text="Кнопка «Стать членом прихода» ведёт сюда.",
    )
    realm_embed_code = models.TextField(
        "HTML-код виджета Realm", blank=True,
        help_text="Необязательно: вставить iframe/виджет онлайн-пожертвований, если Realm его даёт.",
    )

    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"


class PageText(models.Model):
    """
    An editable block of a static template, seeded from the template's own default
    text on first render and thereafter edited from the admin — see
    core/templatetags/editable.py. Lets long-form pages (parish history, about
    text) be admin-editable without a bespoke model per page.
    """

    page = models.SlugField(max_length=100)
    block = models.SlugField(max_length=100)
    label = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("page", "block")
        verbose_name = "Редактируемый блок"
        verbose_name_plural = "Редактируемые блоки"

    def __str__(self):
        return self.label or f"{self.page}:{self.block}"


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    link_url = models.URLField(blank=True)
    link_text = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"

    def __str__(self):
        return self.title


class ClergyMember(models.Model):
    name = models.CharField(max_length=200)
    title = models.CharField("Сан / должность", max_length=200)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="clergy/", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Клирик"
        verbose_name_plural = "Духовенство"

    def __str__(self):
        return self.name


class FirstVisitPage(SingletonModel):
    """The "coming for the first time?" page — the one that decides whether a
    newcomer walks in or closes the tab. Every block is admin-editable."""

    intro = models.TextField(
        "Приветствие", blank=True,
        help_text="Первые два-три абзаца: кто мы и почему вам здесь рады.",
    )
    when_text = models.CharField(
        "Когда приходить", max_length=300, blank=True,
        help_text="Например «Часы и Литургия — в 9:30 утра по воскресеньям».",
    )
    what_to_expect = models.TextField(
        "Как проходит служба", blank=True,
        help_text="Сколько идёт, на каком языке, что бывает после.",
    )
    practical = models.TextField(
        "Практическое", blank=True,
        help_text="Парковка, как одеться, к кому подойти с вопросом.",
    )
    communion_note = models.TextField(
        "О причастии", blank=True,
        help_text="Кто может причащаться и что сделать заранее.",
    )

    class Meta:
        verbose_name = "Страница «Впервые здесь?»"
        verbose_name_plural = "Страница «Впервые здесь?»"

    def __str__(self):
        return "Впервые здесь?"


class Inquiry(models.Model):
    """A newcomer reaching out from the first-visit page."""

    class About(models.TextChoices):
        ORTHODOX = "orthodox", _("Я православный христианин")
        CURIOUS = "curious", _("Я не православный, но хочу узнать больше")
        PRIEST = "priest", _("Хочу поговорить со священником")

    class Contact(models.TextChoices):
        EMAIL = "email", _("Электронная почта")
        PHONE = "phone", _("Телефон")
        EITHER = "either", _("Всё равно")

    name = models.CharField(_("Имя"), max_length=200)
    email = models.EmailField(_("E-mail"), blank=True)
    phone = models.CharField(_("Телефон"), max_length=50, blank=True)
    about = models.CharField(_("О себе"), max_length=20, choices=About.choices)
    preferred_contact = models.CharField(
        _("Как удобнее связаться"), max_length=20, choices=Contact.choices, default=Contact.EITHER
    )
    best_time = models.CharField(_("Удобное время"), max_length=200, blank=True)
    message = models.TextField(_("Сообщение"), blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_handled = models.BooleanField("Отвечено", default=False)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Обращение новичка"
        verbose_name_plural = "Обращения новичков"

    def __str__(self):
        return f"{self.name} — {self.get_about_display()}"


class DonationPage(SingletonModel):
    intro = models.TextField(
        "Вступление", blank=True,
        help_text="Коротко: на что идут пожертвования.",
    )

    class Meta:
        verbose_name = "Страница пожертвований"
        verbose_name_plural = "Страница пожертвований"

    def __str__(self):
        return "Пожертвования"


class DonationMethod(models.Model):
    """One way to give — Realm, PayPal, Zelle, a cheque by post. Ordered list,
    so the parish can add or retire a channel without a developer."""

    page = models.ForeignKey(DonationPage, on_delete=models.CASCADE, related_name="methods")
    title = models.CharField("Название", max_length=120)
    description = models.TextField("Пояснение", blank=True)
    url = models.URLField("Ссылка", blank=True)
    button_label = models.CharField("Надпись на кнопке", max_length=60, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Способ пожертвования"
        verbose_name_plural = "Способы пожертвования"

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения с сайта"

    def __str__(self):
        return f"{self.name} — {self.submitted_at:%d.%m.%Y}"
