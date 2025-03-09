# models.py
from django.db import models

class Note(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255, unique=True)
    contents = models.TextField()
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return "[note]" + self.title

    def display_title(self):
        if self.title.startswith("[autotitle] "):
            return ""
        return self.title

