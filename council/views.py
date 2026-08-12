import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ministries.models import Ministry, MinistryMembership

from .access import (
    account_approver_required,
    can_approve_accounts,
    can_send_mailings,
    council_member_required,
    is_council_member,
    mailing_sender_required,
    portal_member_required,
    targetable_ministries,
    visible_queryset,
)
from .forms import (
    ActionItemForm,
    MailingForm,
    MeetingForm,
    MembershipRequestForm,
    ProtocolForm,
    ReportForm,
)
from .models import (
    ActionItem,
    CouncilProject,
    GroupMailing,
    GroupMailingAttachment,
    Meeting,
    MeetingDocument,
    MembershipRequest,
    Protocol,
    Report,
)


# ---------------------------------------------------------------- access flow

@login_required
def pending(request):
    """Shown to a signed-in user whose request has not been approved yet."""
    req = MembershipRequest.objects.filter(user=request.user).first()
    return render(request, "council/pending.html", {"membership_request": req})


@login_required
def request_access(request):
    """Ask the council for portal access."""
    existing = MembershipRequest.objects.filter(user=request.user).first()
    if existing:
        return redirect("council:pending")

    if request.method == "POST":
        form = MembershipRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
            req.save()
            messages.success(request, "Заявка отправлена. Совет её рассмотрит.")
            return redirect("council:pending")
    else:
        form = MembershipRequestForm()
    return render(request, "council/request_access.html", {"form": form})


@account_approver_required
def approvals(request):
    """Queue of registrations waiting for a decision."""
    pending_requests = MembershipRequest.objects.filter(
        status=MembershipRequest.Status.PENDING
    ).select_related("user")

    if request.method == "POST":
        req = get_object_or_404(MembershipRequest, pk=request.POST.get("request_id"))
        action = request.POST.get("action")
        if action in ("parishioner", "council"):
            req.status = MembershipRequest.Status.APPROVED
            req.is_council_member = action == "council"
            req.approved_by = request.user
            req.approved_at = timezone.now()
            req.save()
            messages.success(request, f"{req.user} принят(а).")
        elif action == "reject":
            req.status = MembershipRequest.Status.REJECTED
            req.save()
            messages.info(request, f"Заявка {req.user} отклонена.")
        return redirect("council:approvals")

    return render(request, "council/approvals.html", {"requests": pending_requests})


# ------------------------------------------------------------------ dashboard

@portal_member_required
def dashboard(request):
    today = timezone.now().date()
    user = request.user

    upcoming = Meeting.objects.filter(
        status=Meeting.Status.PLANNED, date__gte=today
    ).order_by("date")[:3]

    my_tasks = ActionItem.objects.filter(
        assignee=user, status=ActionItem.Status.OPEN
    ).select_related("meeting", "ministry")[:8]

    return render(request, "council/dashboard.html", {
        "upcoming_meetings": upcoming,
        "recent_protocols": visible_queryset(Protocol.objects.all(), user)[:5],
        "recent_reports": visible_queryset(Report.objects.all(), user)[:5],
        "my_tasks": my_tasks,
        "overdue_count": sum(1 for t in my_tasks if t.is_overdue),
        "is_council": is_council_member(user),
        "can_approve": can_approve_accounts(user),
        "can_mail": can_send_mailings(user),
        "pending_count": MembershipRequest.objects.filter(
            status=MembershipRequest.Status.PENDING
        ).count() if can_approve_accounts(user) else 0,
    })


# ------------------------------------------------------------------- meetings

@portal_member_required
def meeting_list(request):
    today = timezone.now().date()
    meetings = Meeting.objects.all()
    return render(request, "council/meeting_list.html", {
        "upcoming": meetings.filter(status=Meeting.Status.PLANNED, date__gte=today).order_by("date"),
        "past": meetings.exclude(status=Meeting.Status.PLANNED, date__gte=today),
        "is_council": is_council_member(request.user),
    })


@portal_member_required
def meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    user = request.user
    return render(request, "council/meeting_detail.html", {
        "meeting": meeting,
        "protocols": visible_queryset(meeting.protocols.all(), user),
        "documents": visible_queryset(meeting.documents.all(), user),
        "tasks": meeting.action_items.all(),
        "is_council": is_council_member(user),
    })


@council_member_required
def meeting_form(request, pk=None):
    meeting = get_object_or_404(Meeting, pk=pk) if pk else None
    if request.method == "POST":
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            meeting = form.save()
            messages.success(request, "Заседание сохранено.")
            return redirect("council:meeting_detail", pk=meeting.pk)
    else:
        form = MeetingForm(instance=meeting)
    return render(request, "council/meeting_form.html", {"form": form, "meeting": meeting})


# ------------------------------------------------------- protocols & reports

@portal_member_required
def protocol_list(request):
    return render(request, "council/protocol_list.html", {
        "protocols": visible_queryset(Protocol.objects.all(), request.user).select_related("meeting"),
        "is_council": is_council_member(request.user),
    })


@portal_member_required
def protocol_detail(request, pk):
    protocol = get_object_or_404(visible_queryset(Protocol.objects.all(), request.user), pk=pk)
    return render(request, "council/protocol_detail.html", {
        "protocol": protocol, "tasks": protocol.action_items.all(),
    })


@council_member_required
def protocol_form(request, pk=None):
    protocol = get_object_or_404(Protocol, pk=pk) if pk else None
    if request.method == "POST":
        form = ProtocolForm(request.POST, request.FILES, instance=protocol)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.created_by_id:
                obj.created_by = request.user
            obj.save()
            messages.success(request, "Протокол сохранён.")
            return redirect("council:protocol_detail", pk=obj.pk)
    else:
        form = ProtocolForm(instance=protocol)
    return render(request, "council/protocol_form.html", {"form": form, "protocol": protocol})


@portal_member_required
def report_list(request):
    return render(request, "council/report_list.html", {
        "reports": visible_queryset(Report.objects.all(), request.user),
        "is_council": is_council_member(request.user),
    })


@council_member_required
def report_form(request, pk=None):
    report = get_object_or_404(Report, pk=pk) if pk else None
    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            obj = form.save(commit=False)
            if not obj.created_by_id:
                obj.created_by = request.user
            obj.save()
            messages.success(request, "Отчёт сохранён.")
            return redirect("council:report_list")
    else:
        form = ReportForm(instance=report)
    return render(request, "council/report_form.html", {"form": form, "report": report})


# ---------------------------------------------------------------------- tasks

@portal_member_required
def task_list(request):
    tasks = ActionItem.objects.select_related("assignee", "meeting", "ministry")
    scope = request.GET.get("scope", "mine")
    if scope == "mine":
        tasks = tasks.filter(assignee=request.user)
    # Счёт открытых берётся до фильтра «показать выполненные»: заголовок
    # отвечает на вопрос «сколько за мной висит», а не «сколько строк на экране».
    open_count = tasks.filter(status=ActionItem.Status.OPEN).count()
    if request.GET.get("show") != "all":
        tasks = tasks.filter(status=ActionItem.Status.OPEN)
    return render(request, "council/task_list.html", {
        "tasks": tasks,
        "scope": scope,
        "show": request.GET.get("show", "open"),
        "open_count": open_count,
        "is_council": is_council_member(request.user),
    })


@council_member_required
def task_form(request, pk=None):
    task = get_object_or_404(ActionItem, pk=pk) if pk else None
    if request.method == "POST":
        form = ActionItemForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Поручение сохранено.")
            return redirect("council:task_list")
    else:
        form = ActionItemForm(instance=task)
    return render(request, "council/task_form.html", {"form": form, "task": task})


@portal_member_required
def task_toggle(request, pk):
    task = get_object_or_404(ActionItem, pk=pk)
    if request.method == "POST" and (
        is_council_member(request.user) or task.assignee_id == request.user.id
    ):
        task.status = (
            ActionItem.Status.OPEN
            if task.status == ActionItem.Status.DONE
            else ActionItem.Status.DONE
        )
        task.save(update_fields=["status"])
    return redirect(request.META.get("HTTP_REFERER") or "council:task_list")


# ------------------------------------------------------------------- projects

@portal_member_required
def project_list(request):
    return render(request, "council/project_list.html", {
        "projects": CouncilProject.objects.select_related("owner"),
        "is_council": is_council_member(request.user),
    })


# -------------------------------------------------------------------- mailing

@mailing_sender_required
def mailing(request):
    ministries = targetable_ministries(request.user)
    if request.method == "POST":
        form = MailingForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            sent = _send_mailing(request, form)
            messages.success(request, f"Отправлено получателям: {sent}.")
            return redirect("council:mailing")
    else:
        form = MailingForm(user=request.user)
    return render(request, "council/mailing.html", {
        "form": form,
        "ministries": ministries,
        "history": GroupMailing.objects.select_related("ministry", "sent_by")[:20],
    })


def _recipients_for(audience, ministry):
    """Email addresses for an audience, de-duplicated and without blanks."""
    from django.contrib.auth.models import User

    if audience == GroupMailing.Audience.MINISTRY and ministry:
        emails = User.objects.filter(
            Q(ministry_memberships__ministry=ministry,
              ministry_memberships__status=MinistryMembership.Status.ACTIVE)
            | Q(led_ministries=ministry)
        ).values_list("email", flat=True)
    else:
        group = (
            "Совет прихода" if audience == GroupMailing.Audience.COUNCIL else "Прихожанин"
        )
        emails = User.objects.filter(groups__name=group).values_list("email", flat=True)
    return sorted({e for e in emails if e})


def _send_mailing(request, form):
    audience = form.cleaned_data["audience"]
    ministry = form.cleaned_data.get("ministry")
    recipients = _recipients_for(audience, ministry)

    mailing_obj = GroupMailing.objects.create(
        audience=audience, ministry=ministry,
        subject=form.cleaned_data["subject"], body=form.cleaned_data["body"],
        sent_by=request.user, recipient_count=len(recipients),
    )
    for f in request.FILES.getlist("attachments"):
        GroupMailingAttachment.objects.create(mailing=mailing_obj, file=f, original_name=f.name)

    if recipients:
        msg = EmailMessage(
            subject=form.cleaned_data["subject"],
            body=form.cleaned_data["body"],
            to=[],            # everyone goes in BCC — nobody's address is exposed
            bcc=recipients,
        )
        for attachment in mailing_obj.attachments.all():
            attachment.file.open("rb")
            msg.attach(attachment.original_name or attachment.file.name, attachment.file.read())
            attachment.file.close()
        msg.send(fail_silently=True)
    return len(recipients)


# --------------------------------------------------------------- file serving

def _serve(filefield):
    if not filefield:
        raise Http404
    storage = filefield.storage
    if not storage.exists(filefield.name):
        raise Http404
    return FileResponse(
        storage.open(filefield.name, "rb"),
        as_attachment=True,
        filename=filefield.name.rsplit("/", 1)[-1],
    )


@portal_member_required
def protocol_download(request, pk):
    obj = get_object_or_404(visible_queryset(Protocol.objects.all(), request.user), pk=pk)
    return _serve(obj.file)


@portal_member_required
def report_download(request, pk):
    obj = get_object_or_404(visible_queryset(Report.objects.all(), request.user), pk=pk)
    return _serve(obj.file)


@portal_member_required
def document_download(request, pk):
    obj = get_object_or_404(visible_queryset(MeetingDocument.objects.all(), request.user), pk=pk)
    return _serve(obj.file)
