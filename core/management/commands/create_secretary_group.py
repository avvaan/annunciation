from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

# (app_label, model_name) -> which actions the parish secretary gets.
# Singletons (SiteSettings/BuildingProject/RussianSchoolPage) only need "change" —
# their admin blocks add/delete anyway (see has_add_permission/has_delete_permission).
GROUP_NAME = "Секретарь"

FULL_ACCESS_MODELS = [
    ("core", "announcement"),
    ("core", "clergymember"),
    ("services", "serviceday"),
    ("services", "serviceitem"),
    ("services", "recurringservicerule"),
    ("services", "recurringserviceitem"),
    ("publications", "publication"),
    ("building", "buildingprojectupdate"),
    ("building", "buildingprojectphoto"),
    ("school", "russianschoolphoto"),
    ("history", "historymilestone"),
]

CHANGE_ONLY_MODELS = [
    ("core", "pagetext"),
    ("core", "sitesettings"),
    ("building", "buildingproject"),
    ("school", "russianschoolpage"),
]

VIEW_ONLY_MODELS = [
    ("core", "contactmessage"),
    ("newsletter", "subscriber"),
]


class Command(BaseCommand):
    help = "Create/update the 'Секретарь' group: day-to-day content editing without full admin access."

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name=GROUP_NAME)
        perms = []

        for app_label, model in FULL_ACCESS_MODELS:
            for action in ("add", "change", "delete", "view"):
                perms.append(self._perm(app_label, model, action))

        for app_label, model in CHANGE_ONLY_MODELS:
            for action in ("change", "view"):
                perms.append(self._perm(app_label, model, action))

        for app_label, model in VIEW_ONLY_MODELS:
            for action in ("view", "change"):
                perms.append(self._perm(app_label, model, action))

        perms = [p for p in perms if p is not None]
        group.permissions.set(perms)
        self.stdout.write(self.style.SUCCESS(
            f"Группа «{GROUP_NAME}» настроена: {len(perms)} прав доступа."
        ))

    def _perm(self, app_label, model, action):
        codename = f"{action}_{model}"
        try:
            return Permission.objects.get(content_type__app_label=app_label, codename=codename)
        except Permission.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"Право {app_label}.{codename} не найдено — пропущено."))
            return None
