from django.core.management.base import BaseCommand, CommandError
from gui.models import Sentence, SeedRegex, SentenceSeedRegex
from accounts.models import CustomUser
from accounts.forms import SignUpForm
import random


class Command(BaseCommand):
    help = 'Generate test user'
    username = 'testuser'
    password = 'rtyuifghjghgh'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', type=str, default=None)

    def handle(self, *args, **options):
        username = options.get('username', self.username)
        form = SignUpForm({
            "first_name": "Test",
            "last_name": "User",
            "username": username,
            "email": "testuser@example.com",
            "password1": self.password,
            "password2": self.password
        })
        try:
            if form.is_valid():
                form.save()
                self.stdout.write(self.style.SUCCESS('Created user: %s' % username))
            else:
                print(form.cleaned_data["password1"])
                raise ValueError("User signup form is not valid %s" % form.error_messages)
        except Exception as e:
            self.stdout.write(self.style.ERROR("Could not create test user! %s" % e))
