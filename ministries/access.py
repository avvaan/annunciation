def visible_document_qs(qs, ministry, user):
    """Filter a MinistryDocument/MinistryReport queryset by visibility against user's tier."""
    if ministry.is_leader(user):
        return qs
    if ministry.is_member(user):
        return qs.exclude(visibility="leaders")
    return qs.filter(visibility="all")


def is_any_ministry_leader(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    from .models import Ministry, MinistryMembership

    return Ministry.objects.filter(leaders=user).exists() or MinistryMembership.objects.filter(
        user=user, role=MinistryMembership.Role.LEADER, status=MinistryMembership.Status.ACTIVE
    ).exists()
