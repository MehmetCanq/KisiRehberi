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

    @action(detail=False, methods=['post'])
    def rename_tag(self, request):
        old_name = request.data.get('old_name')
        new_name = request.data.get('new_name')
        if not old_name or not new_name:
            return Response({"error": "old_name ve new_name alanları zorunludur."}, status=400)
        Contact.objects.filter(user=request.user, tag=old_name).update(tag=new_name)
        return Response({"message": f"'{old_name}' grubu başarıyla '{new_name}' olarak güncellendi."})

    @action(detail=False, methods=['post'])
    def delete_tag(self, request):
        tag_name = request.data.get('tag_name')
        if not tag_name:
            return Response({"error": "tag_name alanı zorunludur."}, status=400)
        Contact.objects.filter(user=request.user, tag=tag_name).update(tag="Diğer")
        return Response({"message": f"'{tag_name}' grubu başarıyla silindi ve kişiler 'Diğer' grubuna aktarıldı."})
