import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'

# Test credentials
credentials = {
    'username': 'testuser',
    'password': 'testpass123'
}

print("🔐 Token almayı test ediyorum...")
try:
    # Token al
    token_response = requests.post(f'{BASE_URL}/token/', json=credentials)
    print(f"Status: {token_response.status_code}")

    if token_response.status_code == 200:
        token_data = token_response.json()
        access_token = token_data.get('access')
        print(f"✅ Token başarıyla alındı!")
        print(f"Access Token: {access_token[:50]}...")

        # Token ile contacts'ı al
        headers = {'Authorization': f'Bearer {access_token}'}
        contacts_response = requests.get(f'{BASE_URL}/contacts/', headers=headers)
        print(f"\n📋 Contacts endpoint kontrol ediliyor...")
        print(f"Status: {contacts_response.status_code}")
        print(f"Response: {json.dumps(contacts_response.json(), indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ Token hatası: {token_response.json()}")

except Exception as e:
    print(f"❌ Hata: {e}")

