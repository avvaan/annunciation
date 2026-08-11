"""Access control for the parish council portal.

Two tiers, granted by group membership:

  Совет прихода  → sees everything, including council-only protocols
                   and financial reports;
  Прихожанин     → sees only what the council marked as shared.

A signed-in user in neither group has registered but is not yet approved and
is shown the "pending" page rather than a 403 — being unapproved is a normal
state, not an error.
"""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from .models import GROUP_COUNCIL, GROUP_PARISHIONER


def is_council_member(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name=GROUP_COUNCIL).exists()
    )


def is_portal_member(user):
    """A council member or an approved parishioner."""
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name__in=[GROUP_COUNCIL, GROUP_PARISHIONER]).exists()
    )


def portal_member_required(view_func):
    """Require an approved portal member; otherwise sign-in or the pending page."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not is_portal_member(request.user):
            return redirect("council:pending")
        return view_func(request, *args, **kwargs)

    return _wrapped


def council_member_required(view_func):
    """Require a council member. Any other signed-in user goes to the
    ministries area, which is open to every registered account."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not is_council_member(request.user):
            return redirect("ministries:ministry_list")
        return view_func(request, *args, **kwargs)

    return _wrapped


def visible_queryset(qs, user):
    """Filter Protocol / Report / MeetingDocument to what `user` may see.

    Council members see everything, drafts included. Parishioners see only
    published items the council chose to share.
    """
    if is_council_member(user):
        return qs
    return qs.filter(is_published=True, council_only=False)


def can_approve_accounts(user):
    """Who may approve a new registration: staff, council members, or any
    ministry leader."""
    from ministries.access import is_any_ministry_leader

    return user.is_authenticated and (
        user.is_staff or is_council_member(user) or is_any_ministry_leader(user)
    )


def can_send_mailings(user):
    """Who may send a group email. A ministry leader may write to their own
    ministry only — enforced per-audience in targetable_ministries()."""
    from ministries.access import is_any_ministry_leader

    return user.is_authenticated and (
        user.is_superuser or is_council_member(user) or is_any_ministry_leader(user)
    )


def targetable_ministries(user):
    """Which ministries this user may write to."""
    from ministries.models import Ministry, MinistryMembership

    qs = Ministry.objects.filter(is_active=True)
    if user.is_superuser or is_council_member(user):
        return qs
    led = list(user.led_ministries.values_list("id", flat=True))
    led += list(
        MinistryMembership.objects.filter(
            user=user,
            role=MinistryMembership.Role.LEADER,
            status=MinistryMembership.Status.ACTIVE,
        ).values_list("ministry_id", flat=True)
    )
    return qs.filter(id__in=set(led))


def mailing_sender_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not can_send_mailings(request.user):
            return redirect("ministries:ministry_list")
        return view_func(request, *args, **kwargs)

    return _wrapped


def account_approver_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not can_approve_accounts(request.user):
            return redirect("ministries:ministry_list")
        return view_func(request, *args, **kwargs)

    return _wrapped
