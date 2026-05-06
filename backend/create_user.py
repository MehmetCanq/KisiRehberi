import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

u, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com'}
)

if created:
    u.set_password('testpass123')
    u.save()
    print(f"✅ Kullanıcı oluşturuldu: {u.username}")
else:
    print(f"✅ Kullanıcı zaten var: {u.username}")
    # Şifreyi set et
    u.set_password('testpass123')
    u.save()
    print(f"✅ Şifre güncellendi")

