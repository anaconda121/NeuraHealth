from django.core.management.base import BaseCommand, CommandError
from django.db.models import FilteredRelation
from django.db import transaction
from django.core.paginator import Paginator
from accounts.models import CustomUser as User
from gui.models import Sentence, SentenceAssignment
from itertools import islice

def split_every(n, iterable):
    iterable = iter(iterable)
    yield from iter(lambda: list(islice(iterable, n)), [])

class DryRunException(Exception):
    pass


"""
"""
class Command(BaseCommand):
    """
    Evenly, randomly assigns all unassigned sentences to all available users, i.e.:
    - 171 unassigned sentences
    - 5 total users
    - Each user gets 34 sentences (171 / 5 = 34.2)
    - 1 sentence remains unassigned

    (slat) [14:43:26] tmck:app git:(feat/assignment-cmd*) $ python manage.py assign_all   
    5 users for 171 available sentences
    Assigning 34 per user
    Assigned 34 sentences to tk123
    Assigned 34 sentences to tk456
    Assigned 34 sentences to tk789
    Assigned 34 sentences to test999
    Assigned 34 sentences to test555
    Exhausted users. Finishing!
    """
    help = 'Assign sentences evenly to all users'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--num-max', type=int, default=None)
        parser.add_argument('-d', '--dry-run', action='store_true')

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        max_num = options.get('num_max')
        try:
            self._assign(dry_run, max_num=max_num)
        except DryRunException:
            self.stdout.write("Dry run finished")
    
    @transaction.atomic
    def _assign(self, dry_run, max_num=None):
        num_users = User.objects.count()
        unassigned = (
            Sentence
                .objects
                .annotate(assignments=FilteredRelation('sentenceassignment'))
                .filter(assignments__isnull=True)
                .order_by('id')
        )
        num_sentences = unassigned.count()
        print(f"{num_users} users for {num_sentences} available sentences")
        if num_sentences < num_users:
            self.stderr.write("Cannot assign sentences, too few sentences available for assignment!")
            return
        if num_sentences == 0:
            self.stderr.write("No sentences available to assign! Aborting!")
            return
        max_per_user = num_sentences // num_users
        if max_num:
            per_user = min(max_per_user, max_num)
        else:
            per_user = max_per_user
        print(f"Assigning {per_user} per user")
        sentence_pages = split_every(per_user, unassigned)
        users = User.objects.all().iterator()
        user = next(users)
        for page in sentence_pages:
            if user:
                for sentence in page:
                    sentence, _ = SentenceAssignment.objects.get_or_create(Sentence=sentence, User=user)
                    sentence.save()
                self.stdout.write(self.style.SUCCESS('Assigned %s sentences to %s' % (len(page), user.username)))
                try:
                    new_user = next(users)
                except StopIteration:
                    new_user = None
                user = new_user
            else:
                print(f"Exhausted users. Finishing!")
        if dry_run:
            raise DryRunException("Dry run aborting")
