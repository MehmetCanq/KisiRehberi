import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

print('📊 DATABASE BİLGİLERİ')
print('=' * 50)
print(f"Engine: {connection.settings_dict['ENGINE']}")
print(f"Database: {connection.settings_dict['NAME']}")
print(f"Host: {connection.settings_dict['HOST']}:{connection.settings_dict['PORT']}")
print()
print('📋 TABLOLAR:')
print('=' * 50)

cursor = connection.cursor()
cursor.execute('''
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
''')

for row in cursor.fetchall():
    print(f'  ✓ {row[0]}')

print()
print('📦 CONTACTS TABLOSU DETAYLARI:')
print('=' * 50)

cursor.execute('''
    SELECT 
        column_name, 
        data_type, 
        is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'contacts_contact'
    ORDER BY ordinal_position
''')

for row in cursor.fetchall():
    nullable = '✓ NULL' if row[2] == 'YES' else '✗ NOT NULL'
    print(f'  {row[0]}: {row[1]} ({nullable})')

print()
print('📊 CONTACTS TABLOSUNDAKI VERİLER:')
print('=' * 50)

cursor.execute('SELECT COUNT(*) FROM contacts_contact')
count = cursor.fetchone()[0]
print(f'Toplam Kişi Sayısı: {count}')

if count > 0:
    cursor.execute('''
        SELECT id, user_id, full_name, phone, email, tag, created_at 
        FROM contacts_contact 
        ORDER BY created_at DESC 
        LIMIT 10
    ''')

    for row in cursor.fetchall():
        print(f'\n  ID: {row[0]} | Kullanıcı: {row[1]} | Ad: {row[2]} | Telefon: {row[3]} | Tag: {row[5]}')

