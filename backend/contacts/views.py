from django.shortcuts import render
from django.db import models
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Contact
from .serializers import ContactSerializer

class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Contact.objects.filter(user=self.request.user)
        tag = self.request.query_params.get('tag')
        if tag and tag != 'Hepsi':
            queryset = queryset.filter(tag=tag)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(full_name__icontains=search) |
                models.Q(phone__icontains=search)
            )
        return queryset.order_by('full_name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def tags(self, request):
        tags_queryset = Contact.objects.filter(user=request.user).values_list('tag', flat=True).distinct()
        default_tags = ["Aile", "İş", "Arkadaş", "Diğer"]
        combined_tags = list(set(default_tags + [t for t in tags_queryset if t]))
        return Response(sorted(combined_tags))
