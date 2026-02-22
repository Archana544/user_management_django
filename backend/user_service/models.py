from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    role = models.CharField(max_length=50, default="user")

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    file_type = models.CharField(max_length=20)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_content = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, default="Pending")  # For DI processing
    json_output = models.JSONField(blank=True, null=True)  # Store structured output
