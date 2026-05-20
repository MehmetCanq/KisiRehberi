from django.shortcuts import render
from django.db import models
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Contact
from .serializers import ContactSerializer

class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Contact.objects.filter(user=self.request.user)
        
        # Etiket filtresi
        tag = self.request.query_params.get('tag')
        if tag and tag != 'Hepsi':
            queryset = queryset.filter(tag=tag)
            
        # Arama filtresi (isim veya telefon numarası)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(full_name__icontains=search) |
                models.Q(phone__icontains=search)
            )
            
        return queryset.order_by('full_name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
