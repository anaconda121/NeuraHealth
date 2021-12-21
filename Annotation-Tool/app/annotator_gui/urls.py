"""annotator_gui URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

# for errors
from django.conf.urls import handler404, handler500, handler403

urlpatterns = [
    # path has route, a string that contains a URL pattern and view. 
    # When Django finds a matching pattern, it calls the specified view \
    # function with an HttpRequest object as the first argument and any “captured” \
    # values from the route as keyword arguments
    path('admin/', admin.site.urls),
    path('', include('gui.urls'))
]

handler404 = 'gui.views.custom_error_404'
handler500 = 'gui.views.custom_error_500'
handler403 = 'gui.views.custom_error_403'