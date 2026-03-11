from django.contrib import admin

from . import models

class NoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'create_time']
    list_display_links = ['title']
    ordering = ['-create_time']
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_public=True)

admin.site.register(models.Note, NoteAdmin)
