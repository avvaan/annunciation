import time

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _

from core.models import SiteSettings

from .forms import CommemorationForm
from .models import Commemoration, CommemorationBatch


def submit(request):
    """Подача записки с сайта."""
    if request.method == "POST":
        form = CommemorationForm(request.POST)
        if form.is_valid():
            note = form.save()
            _notify_parish(note)
            # Человек только что доверил приходу имена своих живых и усопших.
            # Возвращать его к пустой форме с полоской «принято» — значит
            # ответить на это как на подписку в рассылку. Ему нужно увидеть
            # свои имена и узнать, когда их прочтут.
            request.session["last_commemoration"] = note.pk
            return redirect("commemorations:accepted", pk=note.pk)
    else:
        form = CommemorationForm(initial={"form_timestamp": str(time.time())})

    return render(request, "commemorations/submit.html", {
        "form": form,
        "sorokoust_liturgies": Commemoration.SOROKOUST_LITURGIES,
    })


def accepted(request, pk):
    """Подтверждение: имена, как они записаны, и дата ближайшей литургии.

    Открыть можно только ту записку, которую подали в этой сессии: адрес
    вида /commemorations/12/ иначе позволил бы перебором читать чужие
    списки имён вместе с контактами подавшего.
    """
    if request.session.get("last_commemoration") != pk:
        raise Http404
    note = get_object_or_404(Commemoration, pk=pk)
    return render(request, "commemorations/accepted.html", {
        "note": note,
        "next_liturgy": _next_liturgy(),
    })


def _next_liturgy():
    """Ближайший день, где в составе службы есть литургия: записку читают
    на проскомидии, а не на всенощной."""
    from services.models import ServiceDay

    today = timezone.localdate()
    for day in (
        ServiceDay.objects.filter(is_published=True, date__gte=today)
        .prefetch_related("items__service_type").order_by("date")[:30]
    ):
        for item in day.items.all():
            if "литург" in item.service_type.name.lower():
                return day
    return None


def _notify_parish(note):
    """Секретарь узнаёт о записке письмом, а не заглядывая в админку."""
    site = SiteSettings.get_solo()
    if not site.email:
        return
    lines = [
        f"Вид: {note.get_kind_display()}",
        f"Подал: {note.requester_name or '—'}",
        f"Связь: {note.email or '—'} {note.phone or ''}".strip(),
        "",
        f"О здравии ({len(note.living_list)}):",
        note.living_names or "—",
        "",
        f"О упокоении ({len(note.departed_list)}):",
        note.departed_names or "—",
    ]
    if note.notes:
        lines += ["", f"Примечание: {note.notes}"]
    send_mail(
        subject="Новая записка о поминовении",
        message="\n".join(lines),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[site.email],
        fail_silently=True,
    )


def batch_pdf(request, pk):
    """Готовая пачка лежит вне MEDIA_ROOT — отдаём её только сотрудникам."""
    if not (request.user.is_authenticated and request.user.is_staff):
        raise Http404
    batch = CommemorationBatch.objects.filter(pk=pk).first()
    if not batch or not batch.pdf_file:
        raise Http404
    return FileResponse(
        batch.pdf_file.open("rb"),
        as_attachment=True,
        filename=f"zapiski-{batch.pk}.pdf",
    )
