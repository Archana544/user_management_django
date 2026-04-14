from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    role = models.CharField(max_length=50, default="user")

class Document(models.Model):
    STATUS_CHOICES = [
        ("UPLOADED", "Uploaded"),
        ("TEXT_EXTRACTED", "Text Extracted"),
        ("EMBEDDING_CREATED", "Embedding Created"),
        ("INDEXED", "Indexed"),
        ("LLM_RESPONSE_GENERATED", "LLM Response Generated"),
        ("FAILED", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    file_type = models.CharField(max_length=20)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_content = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="processing")  
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    def __str__(self):
        return f"{self.file.name} - {self.user}"