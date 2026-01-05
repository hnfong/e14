from django.db import models
from django.contrib.auth.models import User

def uuid_string():
    import uuid
    return uuid.uuid4().hex

MODEL_CHOICES=["gemma-3-27B", "Kimi-K2", "QwenLong-L1.5-30B-A3B"]

class TextInferenceRequest(models.Model):
    uuid = models.CharField(max_length=36, unique=True, default=uuid_string)
    priority = models.IntegerField(default=50)
    requester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    purpose = models.TextField(blank=True)
    system_prompt = models.TextField(blank=True)
    user_prompt = models.TextField()
    llm_model = models.TextField(default="gemma-3-27B", choices=zip(MODEL_CHOICES, MODEL_CHOICES))
    temperature = models.FloatField(default=0.3)
    max_tokens = models.IntegerField(default=4000)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    llama_cpp_extra_arguments = models.TextField(blank=True) # This field is probably ignored
    worker = models.TextField("The machine that has taken the job", null=True, default=None, blank=True)
    result = models.TextField(blank=True, default="")
    logs = models.TextField(blank=True, default="")
    secrets = models.TextField(blank=True, default="") # Generic field used for authentication later. Leave blank for now
    status = models.IntegerField(default=0)

    STATUS_PENDING = 0
    STATUS_LOCKED = 10
    STATUS_FINALIZED_LINE = 99
    STATUS_DONE = 100
    STATUS_CANCELLED = 101
    STATUS_ERROR = 102

    def __str__(self):
        return f"<TextInferenceRequest - {self.uuid} ({self.created})>"

    @staticmethod
    def list():
        return TextInferenceRequest.objects.all()

    # Pending requests
    @staticmethod
    def list_pending():
        return TextInferenceRequest.list().filter(status=TextInferenceRequest.STATUS_PENDING).order_by('priority', 'created')

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['status', 'priority', 'created']),
            models.Index(fields=['created']),
            models.Index(fields=['priority']),
            models.Index(fields=['result']),
            models.Index(fields=['requester']),
        ]
