from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone

class Entry(models.Model):
    ENTRY_TYPES = (
        ('journal', 'Diary Entry'),  # This is a normal journal entry
        ('comment', 'Encyclopedia Entry'), # The main intent is to comment on the titled subject, and we may add to this as my understanding improves.
        ('archival', 'Archival Comment'), # Mainly used to archive urls, images, etc. that I have seen and have some thoughts about.
    )

    title = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES, default='journal')

    content = models.TextField()

    # space separated tags
    tags = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # For archival entries
    media_file = models.FileField(upload_to='media/journal', blank=True, null=True)

    # Used to store any AI generated stuff
    ai_slop = models.TextField(editable=False, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Journal:{self.id}<{self.title or self.subject or self.content[:50]}>"

