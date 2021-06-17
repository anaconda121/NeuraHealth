from django.core.management.base import BaseCommand, CommandError
from django.db.models import FilteredRelation
from django.db import transaction
from django.core.paginator import Paginator
from accounts.models import CustomUser as User
from gui.models import Sentence, SentenceAssignment, AlwaysRegex, SentenceAnnotation
from itertools import islice

def split_every(n, iterable):
    iterable = iter(iterable)
    yield from iter(lambda: list(islice(iterable, n)), [])

class DryRunException(Exception):
    pass


"""
"""
class Command(BaseCommand):
    help = 'Get some counts'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', type=str, default=None)

    def handle(self, *args, **options):
        self._counts()
        
    
    def _counts(self, username=None):
        num_users = User.objects.count()
        self.stdout.write(f"{num_users} users")
        completed = SentenceAssignment.objects.filter(CompletedAt__isnull=False).count()
        self.stdout.write(f"{completed} completed sentence assignments")
        remaining = SentenceAssignment.objects.filter(CompletedAt__isnull=True).count()
        self.stdout.write(f"{remaining} sentence assignments remain to be completed")
        annotations = SentenceAnnotation.objects
        yes = annotations.filter(Label="YES").count()
        no = annotations.filter(Label="NO").count()
        not_sure = annotations.filter(Label="NTR").count()
        self.stdout.write(f"{yes} Yes Annotations")
        self.stdout.write(f"{no} No Annotations")
        self.stdout.write(f"{not_sure} Not Sure Annotations")
        always_count = AlwaysRegex.objects.count()
        self.stdout.write(f"{always_count} Always Regexes")
        
