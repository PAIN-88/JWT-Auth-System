from rest_framework import serializers
from .models import UserFile


class UserFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = ["id", "file_name", "mime_type", "size_bytes", "uploaded_at"]
        read_only_fields = fields