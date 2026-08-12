from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .access import visible_document_qs
from .forms import (
    MinistryCommentForm,
    MinistryJoinForm,
    MinistryPhotoForm,
    MinistryScheduleEntryForm,
    MinistrySupplyRequestForm,
    MinistryTopicForm,
    SignupForm,
)
from .models import (
    Ministry,
    MinistryComment,
    MinistryDocument,
    MinistryMembership,
    MinistryReport,
    MinistryScheduleEntry,
    MinistrySupplyRequest,
    MinistryTopic,
)


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Добро пожаловать! Теперь можно присоединиться к служениям.")
            return redirect("ministries:ministry_list")
    else:
        form = SignupForm()
    return render(request, "ministries/signup.html", {"form": form})


def ministry_list(request):
    ministries = Ministry.objects.filter(is_active=True)
    my_ids = set()
    if request.user.is_authenticated:
        my_ids = set(
            MinistryMembership.objects.filter(
                user=request.user, status=MinistryMembership.Status.ACTIVE
            ).values_list("ministry_id", flat=True)
        )
    return render(request, "ministries/ministry_list.html", {
        "my_ministries": [m for m in ministries if m.id in my_ids],
        "other_ministries": [m for m in ministries if m.id not in my_ids],
    })


def ministry_detail(request, slug):
    ministry = get_object_or_404(Ministry, slug=slug, is_active=True)
    user = request.user
    is_member = ministry.is_member(user)
    is_leader = ministry.is_leader(user)

    if ministry.is_private and not is_member:
        return render(request, "ministries/ministry_locked.html", {"ministry": ministry})

    if request.method == "POST" and request.user.is_authenticated:
        if "submit_topic" in request.POST and is_member:
            form = MinistryTopicForm(request.POST)
            if form.is_valid():
                topic = form.save(commit=False)
                topic.ministry = ministry
                topic.author = request.user
                topic.save()
                return redirect("ministries:ministry_detail", slug=slug)
        elif "submit_photo" in request.POST and is_member:
            form = MinistryPhotoForm(request.POST, request.FILES)
            if form.is_valid():
                photo = form.save(commit=False)
                photo.ministry = ministry
                photo.uploaded_by = request.user
                photo.save()
                return redirect("ministries:ministry_detail", slug=slug)
        elif "submit_supply" in request.POST and is_member:
            form = MinistrySupplyRequestForm(request.POST)
            if form.is_valid():
                supply = form.save(commit=False)
                supply.ministry = ministry
                supply.requested_by = request.user
                supply.save()
                return redirect("ministries:ministry_detail", slug=slug)
        elif "submit_schedule" in request.POST and is_leader:
            form = MinistryScheduleEntryForm(request.POST)
            if form.is_valid():
                entry = form.save(commit=False)
                entry.ministry = ministry
                entry.save()
                return redirect("ministries:ministry_detail", slug=slug)

    context = {
        "ministry": ministry,
        "is_member": is_member,
        "is_leader": is_leader,
        "membership": ministry.membership_for(user),
        "projects": ministry.projects.all()[:10],
        "topics": ministry.topics.all()[:10],
        "documents": visible_document_qs(ministry.documents.all(), ministry, user),
        "reports": visible_document_qs(ministry.reports.all(), ministry, user),
        "photos": ministry.photos.all()[:12],
        "schedule_entries": ministry.schedule_entries.filter(date__gte=timezone.now().date())[:10],
        "supply_requests": ministry.supply_requests.filter(status=MinistrySupplyRequest.Status.OPEN),
        "topic_form": MinistryTopicForm(),
        "photo_form": MinistryPhotoForm(),
        "supply_form": MinistrySupplyRequestForm(),
        "schedule_form": MinistryScheduleEntryForm(),
        "pending_members": ministry.memberships.filter(
            status=MinistryMembership.Status.PENDING
        ).select_related("user") if is_leader else [],
    }
    # Один адрес — две страницы. Гость решает, вступать ли: ему нужна
    # фотография, рассказ и одна кнопка. Участник пришёл работать: ему
    # нужен график, файлы и заявки, плотно и без витрины.
    template = (
        "ministries/ministry_work.html" if is_member
        else "ministries/ministry_public.html"
    )
    return render(request, template, context)


@login_required
def ministry_join(request, slug):
    ministry = get_object_or_404(Ministry, slug=slug, is_active=True)
    if request.method == "POST":
        form = MinistryJoinForm(request.POST)
        MinistryMembership.objects.get_or_create(
            ministry=ministry, user=request.user,
            defaults={"message": form.data.get("message", "")},
        )
        messages.success(request, "Заявка отправлена, лидер служения её рассмотрит.")
    return redirect("ministries:ministry_detail", slug=slug)


@login_required
def ministry_leave(request, slug):
    ministry = get_object_or_404(Ministry, slug=slug)
    if request.method == "POST":
        MinistryMembership.objects.filter(ministry=ministry, user=request.user).delete()
        ministry.leaders.remove(request.user)
        messages.info(request, "Вы вышли из служения.")
    return redirect("ministries:ministry_detail", slug=slug)


@login_required
def membership_approve(request, pk):
    membership = get_object_or_404(MinistryMembership, pk=pk)
    if request.method == "POST" and membership.ministry.is_leader(request.user):
        membership.status = MinistryMembership.Status.ACTIVE
        membership.approved_by = request.user
        membership.approved_at = timezone.now()
        membership.save()
        messages.success(request, f"{membership.user} принят(а) в служение.")
    return redirect("ministries:ministry_detail", slug=membership.ministry.slug)


@login_required
def topic_detail(request, pk):
    topic = get_object_or_404(MinistryTopic, pk=pk)
    ministry = topic.ministry
    if not ministry.is_member(request.user):
        return render(request, "ministries/ministry_locked.html", {"ministry": ministry})

    if request.method == "POST":
        form = MinistryCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.topic = topic
            comment.author = request.user
            comment.save()
            return redirect("ministries:topic_detail", pk=pk)
    else:
        form = MinistryCommentForm()

    return render(request, "ministries/topic_detail.html", {
        "topic": topic, "ministry": ministry, "comments": topic.comments.all(), "form": form,
    })


@login_required
def supply_toggle(request, pk):
    supply = get_object_or_404(MinistrySupplyRequest, pk=pk)
    if request.method == "POST" and supply.ministry.is_leader(request.user):
        supply.status = MinistrySupplyRequest.Status.DONE
        supply.save(update_fields=["status"])
    return redirect("ministries:ministry_detail", slug=supply.ministry.slug)


def _serve_private_file(request, filefield, ministry):
    if not filefield:
        raise Http404
    storage: FileSystemStorage = filefield.storage
    if not storage.exists(filefield.name):
        raise Http404
    return FileResponse(storage.open(filefield.name, "rb"), as_attachment=True,
                         filename=filefield.name.rsplit("/", 1)[-1])


@login_required
def document_download(request, pk):
    doc = get_object_or_404(MinistryDocument, pk=pk)
    if not visible_document_qs(MinistryDocument.objects.filter(pk=pk), doc.ministry, request.user).exists():
        raise Http404
    return _serve_private_file(request, doc.file, doc.ministry)


@login_required
def report_download(request, pk):
    report = get_object_or_404(MinistryReport, pk=pk)
    if not visible_document_qs(MinistryReport.objects.filter(pk=pk), report.ministry, request.user).exists():
        raise Http404
    return _serve_private_file(request, report.file, report.ministry)
