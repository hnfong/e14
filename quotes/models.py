from django.db import models

class Quote(models.Model):
    content = models.TextField()
    source = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:100]
