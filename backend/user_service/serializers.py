from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Document

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ["id", "title", "file", "file_type", "uploaded_at", "extracted_content"]
        read_only_fields = ["id", "file_type", "uploaded_at"]