from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Contact
from .serializers import ContactSerializer

class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Kullanıcı sadece kendi kontaklarını görebilir"""
        return Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Yeni kontakt kaydedilirken user otomatik atanır"""
        serializer.save(user=self.request.user)
