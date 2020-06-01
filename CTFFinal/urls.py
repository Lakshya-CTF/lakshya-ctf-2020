"""CTF URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
import app.views as views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path


from django.views.generic import TemplateView

handler404 = "app.views.handler404"
handler500 = "app.views.handler500"


urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^$", views.index),
    url(r"^login/", views.teamlogin),
    url(r"^register/", views.register),
    url(r"^quest/", views.quest),
    url(r"^logout/", views.teamlogout),
    url(r"^leaderboard/", views.leaderboard),
    url(r"^timer/", views.timer),
    url(r"^hint/", views.hint),
    url(r"^uservalidator/", views.validate_username),
    url(r"^instructions/", views.instructions),
    url(r"^about/", views.about),
    path("machine/<int:id>", views.machine),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
