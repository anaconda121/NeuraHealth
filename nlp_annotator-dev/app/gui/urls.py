from django.urls import include, path

# for favicon
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about',views.about,name='about'),
    path('search',views.search,name='search'),
    path('consensus',views.group_consensus,name='group_consensus'),
    path('login',views.user_login,name='user_login'),
    path('logout', views.user_logout, name='user_logout'),
    path('profile', views.user_profile, name='user_profile'),
    path('home',views.annotator_home,name='annotator_home'),
    path('highlight',views.highlight_sentence,name='highlight_sentence'),
    path('annotate/<int:patient_id>/<int:local_note_id>',views.show_note,name='show_note'),
    path("favicon.ico", RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")))
]