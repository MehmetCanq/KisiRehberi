from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'full_name', 'phone', 'email', 'note', 'tag', 'created_at', 'user']
        read_only_fields = ['id', 'created_at', 'user']
