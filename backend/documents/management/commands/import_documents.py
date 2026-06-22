from django.core.management.base import BaseCommand, CommandError

from documents.importers import import_document_plan


class Command(BaseCommand):
    help = 'Import document tasks from the gold mining Excel plan.'

    def add_arguments(self, parser):
        parser.add_argument('path', help='Path to .xlsx file')
        parser.add_argument(
            '--year',
            type=int,
            help='Calendar year for deadline cells. If omitted, year is taken from filename.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse file and show statistics without saving changes.',
        )
        parser.add_argument(
            '--no-update',
            action='store_true',
            help='Skip rows that already exist instead of updating them.',
        )

    def handle(self, *args, **options):
        path = options['path']

        try:
            stats = import_document_plan(
                path,
                year=options['year'],
                dry_run=options['dry_run'],
                update_existing=not options['no_update'],
            )
        except FileNotFoundError as exc:
            raise CommandError(f'File not found: {path}') from exc
        except Exception as exc:
            raise CommandError(f'Import failed: {exc}') from exc

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('Dry run: database changes were rolled back.'))

        self.stdout.write(self.style.SUCCESS('Import finished.'))
        self.stdout.write(f'Mining objects created: {stats.mining_objects_created}')
        self.stdout.write(f'Licenses created: {stats.licenses_created}')
        self.stdout.write(f'Directions created: {stats.directions_created}')
        self.stdout.write(f'Authorities created: {stats.authorities_created}')
        self.stdout.write(f'Tasks created: {stats.tasks_created}')
        self.stdout.write(f'Tasks updated: {stats.tasks_updated}')
        self.stdout.write(f'Rows skipped: {stats.rows_skipped}')
