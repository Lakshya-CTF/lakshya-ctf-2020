from django.contrib import admin
from .models import Team, Questions, TeamAdmin, Machines, SolvedTimestamps
from django.contrib.sessions.models import Session

admin.site.site_header = "Lakshya CTF Admin Portal"
admin.site.index_title = "Adminsitration"
admin.site.site_title = "Lakshya CTF | Administration"
# admin.site.login_template = 'app/admin.html'

# Register your models here.
admin.site.register(Team, TeamAdmin)
admin.site.register(Questions)
admin.site.register(Machines)