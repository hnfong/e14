import re

from django.contrib import admin
from django.shortcuts import redirect
from django.utils import timezone

from . import models

DATETIME_TITLE = re.compile(r"(FB|Karp|CT|THR|NQ) (?P<year>[0-9]{4})-(?P<month>[0-9]+)-(?P<day>[0-9]+)")
THREADS_US_DATE = re.compile(r"(?P<month>[0-9]+)/(?P<day>[0-9]+)/(?P<year>[0-9]{2})")
FACEBOOK_DATE = re.compile(r"(?P<month_eng>[a-zA-Z]+) (?P<day>[0-9]+)")

ENGLISH = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".lower().split()
def monthEnglishToInt(monthEnglish):
    return ENGLISH.index(monthEnglish[:3].lower()) + 1

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
    fields = ('title', 'slug', 'entry_type', 'content', 'media_file', 'tags', 'ai_slop', 'is_hidden', 'is_public', 'created_at', 'plain_text' )
    readonly_fields = ('ai_slop', )


    # def get_changeform_initial_data(self, request):
        # return {'title': 'Karp 2025-07-'}

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user

        if change and obj.entry_type in ("topic", "archive"): # change is true if it's an edit
            original_obj = self.model.objects.get(pk=obj.pk)
            if remove_newlines(original_obj.content) != remove_newlines(obj.content):
                now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                obj.content += f"\r\n\r\nEdited: {now}\r\n"

        # Add a prefix to the tags so it's easier to just search for the tag in a generic search bar
        obj.tags = " ".join(f"t:{x}" if not x.startswith("t:") else x for x in (obj.tags or "").split() if x)

        if not obj.tags:
            obj.tags = None

        obj.content = obj.content.lstrip()
        if obj.content.startswith("si.fong"):
            lines = obj.content.split("\n")
            if len(lines) > 1 and (m := THREADS_US_DATE.search(lines[1])):
                obj.title = f"THR 20{m.group('year')}-{m.group('month')}-{m.group('day')}"
                now_time = timezone.now().strftime('%H:%M:%S')
                obj.slug = obj.title.replace(' ', '-').lower() + "--" + str(now_time).replace(":", "-")
                obj.content = "\r\n\r\n".join(line.strip() for line in lines[2:])

        if obj.content.startswith("賞鯉專家"):
            lines = obj.content.split("\n")
            if len(lines) > 1 and (m := FACEBOOK_DATE.search(lines[1])):
                import datetime
                current_year_back = (timezone.now() - datetime.timedelta(days=45)).year
                obj.title = f"Karp {current_year_back}-{'%02d' % monthEnglishToInt(m.group('month_eng'))}-{'%02d' % int(m.group('day'))}"
                now_time = timezone.now().strftime('%H:%M:%S')
                obj.slug = obj.title.replace(' ', '-').lower() + "--" + str(now_time).replace(":", "-")
                obj.content = "\r\n\r\n".join(line.strip() for line in lines[2:])

        if m := DATETIME_TITLE.search(obj.title):
            obj.created_at = obj.created_at.replace(
                year=int(m.group('year')),
                month=int(m.group('month')),
                day=int(m.group('day'))
            )

        super().save_model(request, obj, form, change)

    def response_change(self, request, obj):
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            self.message_user(request, "Entry saved. Returning to entry page.")
            return redirect('journal:view_slug', slug=obj.slug)
        return super().response_change(request, obj)

    def response_add(self, request, obj):
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            self.message_user(request, "Entry saved. Returning to entry page.")
            return redirect('journal:view_slug', slug=obj.slug)
        return super().response_add(request, obj)
