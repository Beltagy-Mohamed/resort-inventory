from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


# Which model-level permissions each group gets. Kept explicit and
# readable rather than "give Staff everything except delete" magic,
# so it's obvious at a glance what each role can do.
STAFF_PERMISSIONS = [
    "view_product", "add_product", "change_product",
    "view_category", "view_color", "view_size",
    "add_inventorytransaction", "view_inventorytransaction",
    "view_activitylog",
]

ADMIN_PERMISSIONS = [
    "view_product", "add_product", "change_product", "delete_product",
    "view_category", "add_category", "change_category", "delete_category",
    "view_color", "add_color", "change_color", "delete_color",
    "view_size", "add_size", "change_size", "delete_size",
    "view_inventorytransaction", "add_inventorytransaction",
    "view_activitylog",
    "view_codesequence",
    "view_systemsettings", "change_systemsettings",
]


class Command(BaseCommand):
    """
    Creates (or updates) the two Groups the app relies on: Admin and
    Staff. Safe to run repeatedly — uses get_or_create and always
    re-syncs the permission set, so it never duplicates a group.

    Usage:
        python manage.py setup_groups
    """

    help = "Create/update the Admin and Staff groups with the correct inventory permissions."

    def _assign(self, group_name, codenames):
        group, created = Group.objects.get_or_create(name=group_name)

        permissions = Permission.objects.filter(
            content_type__app_label="inventory",
            codename__in=codenames,
        )

        found_codenames = set(permissions.values_list("codename", flat=True))
        missing = set(codenames) - found_codenames
        if missing:
            self.stdout.write(self.style.WARNING(
                f"  ! {group_name}: permission codename(s) not found, skipped: {sorted(missing)}"
            ))

        group.permissions.set(permissions)

        verb = "created" if created else "updated"
        self.stdout.write(f"  {group_name} group {verb} with {permissions.count()} permission(s).")

    def handle(self, *args, **options):
        self._assign("Staff", STAFF_PERMISSIONS)
        self._assign("Admin", ADMIN_PERMISSIONS)

        self.stdout.write(self.style.SUCCESS(
            "Done. Assign a user to 'Admin' or 'Staff' via /admin/auth/user/, "
            "or create one with: python manage.py createsuperuser"
        ))
