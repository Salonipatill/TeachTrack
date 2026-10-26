from django.core.management.base import BaseCommand
from ClassApp.models import Student,Faculty,Director,Submission,Doubt,Rating
class Command(BaseCommand):
    help='List migrated role-record IDs and login usernames without displaying passwords.'
    def handle(self,*args,**opts):
        for model,role in [(Student,'student'),(Faculty,'faculty'),(Director,'director')]:
            for item in model.objects.select_related('user').order_by('pk'):
                self.stdout.write(f'{role} #{item.pk}: {item.user.username if item.user_id else "UNLINKED"}')
        for model in [Submission,Doubt,Rating]:
            self.stdout.write(f'{model.__name__}: {model.objects.filter(student__isnull=True).count()} historical rows without a verified student link')
