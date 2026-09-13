from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import LeadershipAccessConfig

class Command(BaseCommand):
    help = 'نقل صلاحية قسم أصناف القائد إلى مستخدم آخر'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, required=True, help='ID للمستخدم الجديد')
        parser.add_argument('--note', type=str, required=True, help='سبب النقل')

    def handle(self, *args, **options):
        user_id = options['user_id']
        note = options['note']

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'لا يوجد مستخدم بهذا المعرف {user_id}'))
            return

        config, created = LeadershipAccessConfig.objects.get_or_create(id=1, defaults={'holder': user})
        if not created:
            old_user = config.holder
            config.holder = user
            config.granted_by_note = note
            config.save()
            self.stdout.write(self.style.SUCCESS(f'تم نقل الصلاحية من {old_user.username} إلى {user.username}. السبب: {note}'))
        else:
            config.granted_by_note = note
            config.save()
            self.stdout.write(self.style.SUCCESS(f'تم منح الصلاحية بنجاح إلى {user.username}. السبب: {note}'))
