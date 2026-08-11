from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MembershipRequest, sync_portal_groups


@receiver(post_save, sender=MembershipRequest)
def sync_groups_on_save(sender, instance, **kwargs):
    """Keep portal groups in step with the request's status.

    Wired to the signal rather than to the admin form, so a change made from
    a bulk action, the shell or a data migration grants the same access as one
    made through the admin. The status is the only source of truth.
    """
    sync_portal_groups(instance)
