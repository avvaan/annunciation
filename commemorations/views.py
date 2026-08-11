import time

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
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
            messages.success(
                request,
                _("Записка принята. Имена будут помянуты на ближайшей литургии."),
            )
            return redirect("commemorations:submit")
    else:
        form = CommemorationForm(initial={"form_timestamp": str(time.time())})

    return render(request, "commemorations/submit.html", {
        "form": form,
        "sorokoust_liturgies": Commemoration.SOROKOUST_LITURGIES,
    })


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
