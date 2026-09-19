from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Creates a new LeaderStaff user and adds them to the LeaderStaff group.

    Usage:
        python manage.py create_leader_staff --username=ahmed --password=Secret123
        python manage.py create_leader_staff --username=ahmed  (prompts for password)
    """

    help = "Create a new LeaderStaff user (manager of the leader warehouse section)."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True, help="Username for the new LeaderStaff member.")
        parser.add_argument("--password", default=None, help="Password (will prompt if not provided).")
        parser.add_argument("--email", default="", help="Email address (optional).")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        email    = options.get("email", "")

        # Make sure LeaderStaff group exists
        group, created = Group.objects.get_or_create(name="LeaderStaff")
        if created:
            self.stdout.write(self.style.WARNING(
                "  LeaderStaff group did not exist and was just created. "
                "Run 'python manage.py setup_groups' to assign correct permissions."
            ))

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            raise CommandError(f"User '{username}' already exists. Use the admin panel to assign them to the LeaderStaff group.")

        # Prompt for password if not provided
        if not password:
            from django.contrib.auth.password_validation import validate_password
            import getpass
            password = getpass.getpass(f"Password for {username}: ")
            try:
                validate_password(password)
            except Exception as e:
                raise CommandError(f"Password validation failed: {e}")

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            is_staff=False,
            is_superuser=False,
        )
        user.groups.add(group)

        self.stdout.write(self.style.SUCCESS(
            f"LeaderStaff user '{username}' created and added to the LeaderStaff group."
        ))
        self.stdout.write(
            "  IMPORTANT: This user can only see and manage leader section items.\n"
            "  They cannot see regular products, reports, or any non-leader data.\n"
            "  Use 'python manage.py transfer_leadership_access' to assign the leader role itself."
        )
