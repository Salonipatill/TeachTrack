from django.core.management.base import BaseCommand,CommandError

from ClassApp.models import Resource
from ClassApp.services import preserve_resource_file


class Command(BaseCommand):
    help='Preserve existing resource files in the database for shared-instance downloads. Defaults to dry-run.'

    def add_arguments(self,parser):
        parser.add_argument('--resource-id',type=int,required=True)
        parser.add_argument('--apply',action='store_true')

    def handle(self,*args,**options):
        try:
            resource=Resource.objects.get(pk=options['resource_id'])
        except Resource.DoesNotExist:
            raise CommandError('Resource does not exist.') from None
        try:
            size=resource.file.size
        except (FileNotFoundError,OSError):
            raise CommandError('The source file is missing. Restore it on this machine before preserving it.') from None
        if size>30*1024*1024:raise CommandError('Resource files must be at most 30 MB.')
        if not options['apply']:
            self.stdout.write(f'Dry-run: resource {resource.pk}, {size} bytes available. No database changes made.')
            return
        try:
            saved=preserve_resource_file(resource)
        except (FileNotFoundError,OSError,ValueError):
            raise CommandError('The source file could not be preserved. No stored copy was replaced.') from None
        self.stdout.write(self.style.SUCCESS(f'Preserved resource {resource.pk}: {len(saved.content)} bytes in the database.'))
