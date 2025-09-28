from django.db import models 

from django.contrib.auth.models import User
from django.utils import timezone

class Entry(models.Model):
    # ENTRY_TYPES = (
        # ('diary', 'Diary Entry'),
        # ('encyclopedia', 'Encyclopedia Entry'),
        # ('archival_comment', 'Archival Comment'),
    # )

    title = models.CharField(max_length=500, blank=True, null=True)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    # entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)

    content = models.TextField()

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # For archival_comment entries
    source_url = models.URLField(blank=True, null=True)
    # media_file = models.FileField(upload_to='archival_media/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Journal:{self.id}<{self.title or self.subject or self.content[:50]}>"

