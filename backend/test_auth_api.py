import requests
import json
import random
import string

BASE_URL = 'http://127.0.0.1:8000/api'

def random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Test data
username = f"user_{random_string(6)}"
email = f"{username}@test.com"
password = "testpassword123"

print("[START] KisiRehberi API Testleri Baslatiliyor...\n")

# 1. Kayit Testi
print(f"[AUTH] 1. Kayit Olunuyor: {username} ({email})...")
register_data = {
    "username": username,
    "email": email,
    "password": password
}
try:
    reg_response = requests.post(f"{BASE_URL}/register/", json=register_data)
    print(f"Status: {reg_response.status_code}")
    print(f"Response: {reg_response.json()}")
    assert reg_response.status_code == 201, "Kayit basarisiz oldu!"
    print("[OK] Kayit basarili!\n")
except Exception as e:
    print(f"[ERROR] Kayit hatasi: {e}")
    exit(1)

# 2. Token / Giris Testi
print("[AUTH] 2. JWT Token Aliniyor (Giris yapiliyor)...")
login_data = {
    "username": username,
    "password": password
}
try:
    token_response = requests.post(f"{BASE_URL}/token/", json=login_data)
    print(f"Status: {token_response.status_code}")
    assert token_response.status_code == 200, "Token alinamadi!"
    
    token_data = token_response.json()
    access_token = token_data.get('access')
    print("[OK] Giris basarili! Token alindi.\n")
except Exception as e:
    print(f"[ERROR] Giris hatasi: {e}")
    exit(1)

headers = {'Authorization': f'Bearer {access_token}'}

# 3. Profil (/me/) Testi
print("[PROFILE] 3. Profil bilgileri sorgulaniyor (/api/me/)...")
try:
    me_response = requests.get(f"{BASE_URL}/me/", headers=headers)
    print(f"Status: {me_response.status_code}")
    print(f"Response: {me_response.json()}")
    assert me_response.status_code == 200, "Profil sorgulama basarisiz!"
    assert me_response.json()['username'] == username, "Profil verileri eslesmiyor!"
    print("[OK] Profil sorgulama basarili!\n")
except Exception as e:
    print(f"[ERROR] Profil hatasi: {e}")
    exit(1)

# 4. Kisi Olusturma Testi
print("[CONTACT] 4. Yeni Kisi Ekleniyor...")
contact_data = {
    "full_name": "Can Yilmaz",
    "phone": "05551112233",
    "email": "canyilmaz@test.com",
    "note": "Universiteden arkadasim",
    "tag": "Arkadas"
}
try:
    contact_response = requests.post(f"{BASE_URL}/contacts/", json=contact_data, headers=headers)
    print(f"Status: {contact_response.status_code}")
    print(f"Response: {json.dumps(contact_response.json(), indent=2, ensure_ascii=False)}")
    assert contact_response.status_code == 201, "Kisi eklenemedi!"
    print("[OK] Kisi basariyla eklendi!\n")
except Exception as e:
    print(f"[ERROR] Kisi ekleme hatasi: {e}")
    exit(1)

# 5. Listeleme ve Arama Testi
print("[SEARCH] 5. Arama & Filtreleme Test Ediliyor...")
try:
    # Arama testi (Can yazarak)
    search_response = requests.get(f"{BASE_URL}/contacts/?search=Can", headers=headers)
    print(f"Arama 'Can' Status: {search_response.status_code}")
    results = search_response.json().get('results', search_response.json())
    print(f"Bulunan Kisi Sayisi: {len(results)}")
    assert len(results) > 0, "Arama sonucu bos cikti!"
    
    # Etiket filtresi testi (Aile filtresi, bos donmeli)
    tag_response = requests.get(f"{BASE_URL}/contacts/?tag=Aile", headers=headers)
    tag_results = tag_response.json().get('results', tag_response.json())
    print(f"Aile Filtresi Bulunan Kisi Sayisi: {len(tag_results)}")
    assert len(tag_results) == 0, "Aile filtresinde kisi bulunmamasi gerekiyordu!"
    
    print("[OK] Arama & Filtreleme testleri basarili!\n")
except Exception as e:
    print(f"[ERROR] Filtreleme hatasi: {e}")
    exit(1)

print("[SUCCESS] Tum API entegrasyon testleri BASARIYLA TAMAMLANDI!")
