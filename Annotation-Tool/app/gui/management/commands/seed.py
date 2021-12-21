from faker import Faker
from django.core.management.base import BaseCommand, CommandError
from gui.models import Sentence, SeedRegex, SentenceSeedRegex
import random


class Command(BaseCommand):
    help = 'Generate random sentences'
    fake = Faker()

    def add_arguments(self, parser):
        parser.add_argument('num', type=int)

    def handle(self, *args, **options):
        if options['num'] < 1:
            self.stdout.write(self.style.ERROR('Number of sentences must be greater than 0!'))
        else:
            for _ in range(options['num']):
                text = self.fake.paragraph(nb_sentences=1, variable_nb_sentences=False)
                sentence = Sentence(Contents=text)
                sentence.save()
                seed_regexes(sentence)
            self.stdout.write(self.style.SUCCESS('Added %s sentences' % options['num']))
        

def seed_regexes(sentence):
    words = sentence.Contents.split()
    k = max(len(words) // 3, 1)
    seed_words = random.sample(words, k)
    for word in seed_words:
        regex, _ = SeedRegex.objects.get_or_create(Pattern=word)
        assoc = SentenceSeedRegex(Sentence=sentence, SeedRegex=regex)
        assoc.save()