from django.core.management.base import BaseCommand, CommandError
from accounts.models import CustomUser as User
from gui.models import Sentence, SentenceAssignment
from ._load_data import load_data

class Command(BaseCommand):
    help = 'Assign random sentences'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)
        parser.add_argument('-s', '--start_row', type=int, default=1)

    def handle(self, *args, **options):
        try:
            print(f"Starting from row {options['start_row']}")
            load_data(options['filename'], options['start_row'])
        except Exception as e:
            self.stderr.write("Encountered error %s" % e)
            raise
        self.stdout.write("Finished!")
                