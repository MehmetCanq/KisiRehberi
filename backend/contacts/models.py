from django.db import models
from django.contrib.auth.models import User

class Contact(models.Model):
    # Kişiyin sahibi kullanıcı
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")
    
    # Zorunlu 
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    
    # Opsiyonel 
    email = models.EmailField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    
    # Etiket 
    tag = models.CharField(max_length=50, default="Diğer")
    
    # Kayıt tarihi
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.phone})"
# Create your models here.
