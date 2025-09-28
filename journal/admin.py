from django.contrib import admin
from django.shortcuts import redirect
from django.utils import timezone

from . import models

def remove_newlines(s):
    # Between the django-editor and the browser, sometimes newlines are changed
    # (eg. '\n' => '\r\n') without the user actively editing it. This leads to
    # unexpected behavior when checking whether the field has changed.
    return s.replace('\n', '').replace('\r', '')

@admin.register(models.Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'tags', 'created_at', 'updated_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-created_at']
    fields = ('title', 'slug', 'entry_type', 'content', 'media_file', 'tags', 'ai_slop', 'is_hidden', 'is_public' )
    readonly_fields = ('ai_slop', )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        if change:  # This is an edit, not a new entry
            original_obj = self.model.objects.get(pk=obj.pk)
            if remove_newlines(original_obj.content) != remove_newlines(obj.content):
                now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                obj.content += f"\r\n\r\nEdited: {now}\r\n"

        # Add a prefix to the tags so it's easier to just search for the tag in a generic search bar
        obj.tags = " ".join(f"t:{x}" if not x.startswith("t:") else x for x in (obj.tags or "").split() if x)
        if not obj.tags:
            obj.tags = None
        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        # 🤖🤖🤖
        if "_continue" not in request.POST and "_saveasnew" not in request.POST:
            self.message_user(request, "Entry saved. Returning to entry page.")
            return redirect('view_slug', slug=obj.slug)
        return super().response_change(request, obj)
