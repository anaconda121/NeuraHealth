from django.test import TestCase, Client, RequestFactory
from django.shortcuts import reverse
from accounts.models import CustomUser
from gui.models import PatientDemographic
from gui.views import annotator_home, user_profile


class GuiViewsTests(TestCase):
    pass