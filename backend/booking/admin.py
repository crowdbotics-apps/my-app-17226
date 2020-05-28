from django.contrib import admin

from .models import Bookable, BookableInput, BookedService


admin.site.register(Bookable)
admin.site.register(BookableInput)
admin.site.register(BookedService)
