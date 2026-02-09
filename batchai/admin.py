from django.contrib import admin

from . import models

class TextInferenceRequestAdmin(admin.ModelAdmin):
    save_as = True

admin.site.register(models.TextInferenceRequest, TextInferenceRequestAdmin)
