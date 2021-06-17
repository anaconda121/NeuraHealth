from faker import Faker
from django.core.management.base import BaseCommand, CommandError
from accounts.models import CustomUser as User
from gui.models import Sentence, SentenceAssignment

class Command(BaseCommand):
    help = 'Assign random sentences'
    fake = Faker()

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('num', type=int)

    def handle(self, *args, **options):
        user = User.objects.get(username=options['username'])
        sentences = Sentence.objects.order_by("?")[:options['num']]
        if not sentences:
            self.stdout.write(self.style.ERROR('No sentences to assign!'))
        else:    
            for sentence in sentences:
                sentence, _ = SentenceAssignment.objects.get_or_create(Sentence=sentence, User=user)
                sentence.save()
            self.stdout.write(self.style.SUCCESS('Assigned %s sentences to %s' % (options['num'], user.username)))
            