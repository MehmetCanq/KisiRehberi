<script setup>
import { ref, onMounted, watch } from "vue";
import api from './api.js';

// State
const contacts = ref([]);
const loading = ref(false);
const isAuthenticated = ref(false);
const authTab = ref('login'); // 'login' or 'register'
const currentUser = ref(null);

// Forms
const loginForm = ref({ username: '', password: '' });
const registerForm = ref({ username: '', email: '', password: '' });
const authErrors = ref({});

const newContact = ref({ full_name: '', phone: '', email: '', note: '', tag: 'Arkadaş' });
const editContactData = ref({ id: null, full_name: '', phone: '', email: '', note: '', tag: '' });

// Search & Filtering
const searchQuery = ref('');
const selectedTag = ref('Hepsi');
const tags = ['Hepsi', 'Aile', 'İş', 'Arkadaş', 'Diğer'];

// Pagination
const currentPage = ref(1);
const totalPages = ref(1);

// Modals
const activeModal = ref(null); // 'create', 'edit', 'detail', 'delete'
const selectedContact = ref(null);

// Toasts
const toasts = ref([]);
const addToast = (message, type = 'success') => {
  const id = Date.now() + Math.random();
  toasts.value.push({ id, message, type });
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id);
  }, 3500);
};

// Auth Actions
const fetchCurrentUser = async () => {
  try {
    const response = await api.get('me/');
    currentUser.value = response.data;
  } catch (error) {
    console.error('Kullanıcı bilgisi alınamadı:', error);
  }
};

const handleLogin = async () => {
  authErrors.value = {};
  if (!loginForm.value.username || !loginForm.value.password) {
    addToast('Kullanıcı adı ve şifre gereklidir.', 'error');
    return;
  }
  try {
    const response = await api.post('token/', {
      username: loginForm.value.username,
      password: loginForm.value.password
    });
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    isAuthenticated.value = true;
    addToast('Giriş başarılı! Hoş geldiniz.', 'success');
    loginForm.value = { username: '', password: '' };
    await fetchCurrentUser();
    await fetchContacts();
  } catch (error) {
    const detail = error.response?.data?.detail || 'Giriş yapılamadı. Bilgilerinizi kontrol edin.';
    addToast(detail, 'error');
  }
};

const handleRegister = async () => {
  authErrors.value = {};
  if (!registerForm.value.username || !registerForm.value.email || !registerForm.value.password) {
    addToast('Lütfen tüm alanları doldurun.', 'error');
    return;
  }
  try {
    await api.post('register/', registerForm.value);
    addToast('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success');
    // Giriş sekmesine geçip kullanıcı adını hazır getir
    loginForm.value.username = registerForm.value.username;
    authTab.value = 'login';
    registerForm.value = { username: '', email: '', password: '' };
  } catch (error) {
    if (error.response?.data) {
      authErrors.value = error.response.data;
      const firstErrorKey = Object.keys(error.response.data)[0];
      const errorMsg = error.response.data[firstErrorKey];
      addToast(Array.isArray(errorMsg) ? errorMsg[0] : errorMsg, 'error');
    } else {
      addToast('Kayıt sırasında bir hata oluştu.', 'error');
    }
  }
};

const handleLogout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  isAuthenticated.value = false;
  currentUser.value = null;
  contacts.value = [];
  addToast('Oturum kapatıldı.', 'info');
};

// Contact CRUD Actions
const fetchContacts = async (page = 1) => {
  loading.value = true;
  try {
    const response = await api.get('contacts/', {
      params: {
        page: page,
        search: searchQuery.value,
        tag: selectedTag.value
      }
    });
    if (response.data.results !== undefined) {
      contacts.value = response.data.results;
      const count = response.data.count || 0;
      totalPages.value = Math.ceil(count / 10) || 1;
    } else {
      contacts.value = response.data;
      totalPages.value = 1;
    }
    currentPage.value = page;
  } catch (error) {
    console.error('Kişiler çekilemedi:', error);
    addToast('Kişi listesi yüklenirken hata oluştu.', 'error');
  } finally {
    loading.value = false;
  }
};

const handleCreateContact = async () => {
  if (!newContact.value.full_name || !newContact.value.phone) {
    addToast('İsim ve Telefon alanları zorunludur.', 'error');
    return;
  }
  try {
    await api.post('contacts/', newContact.value);
    addToast('Kişi başarıyla eklendi.', 'success');
    closeModal();
    newContact.value = { full_name: '', phone: '', email: '', note: '', tag: 'Arkadaş' };
    await fetchContacts(1); // Yenileyip sayfa 1'e git
  } catch (error) {
    addToast('Kişi kaydedilirken hata oluştu.', 'error');
  }
};

const handleUpdateContact = async () => {
  if (!editContactData.value.full_name || !editContactData.value.phone) {
    addToast('İsim ve Telefon alanları zorunludur.', 'error');
    return;
  }
  try {
    await api.put(`contacts/${editContactData.value.id}/`, editContactData.value);
    addToast('Kişi başarıyla güncellendi.', 'success');
    closeModal();
    await fetchContacts(currentPage.value);
  } catch (error) {
    addToast('Güncelleme sırasında hata oluştu.', 'error');
  }
};

const handleDeleteContact = async () => {
  if (!selectedContact.value) return;
  try {
    await api.delete(`contacts/${selectedContact.value.id}/`);
    addToast('Kişi rehberden silindi.', 'success');
    closeModal();
    if (contacts.value.length === 1 && currentPage.value > 1) {
      await fetchContacts(currentPage.value - 1);
    } else {
      await fetchContacts(currentPage.value);
    }
  } catch (error) {
    addToast('Silme işlemi sırasında hata oluştu.', 'error');
  }
};

// Modal helpers
const openModal = (type, contact = null) => {
  activeModal.value = type;
  selectedContact.value = contact;
  if (type === 'edit' && contact) {
    editContactData.value = { ...contact };
  }
};

const closeModal = () => {
  activeModal.value = null;
  selectedContact.value = null;
};

// Initials helper
const getInitials = (name) => {
  if (!name) return '?';
  const parts = name.split(' ');
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  return name[0].toUpperCase();
};

// Search Watcher with Debounce
let searchTimeout = null;
watch(searchQuery, () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    fetchContacts(1);
  }, 350);
});

watch(selectedTag, () => {
  fetchContacts(1);
});

// Lifecycle
onMounted(async () => {
  const token = localStorage.getItem('access_token');
  if (token) {
    isAuthenticated.value = true;
    await fetchCurrentUser();
    await fetchContacts();
  }
});
</script>

<template>
  <div class="app-layout">
    <!-- Toast notifications -->
    <div class="toast-container">
      <div v-for="toast in toasts" :key="toast.id" :class="['toast', `toast-${toast.type}`]">
        <span class="toast-icon">
          <svg v-if="toast.type === 'success'" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>
          <svg v-else-if="toast.type === 'error'" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /></svg>
          <svg v-else viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" /></svg>
        </span>
        <span class="toast-message">{{ toast.message }}</span>
      </div>
    </div>

    <!-- 1. AUTHENTICATION SECTION (If not authenticated) -->
    <div v-if="!isAuthenticated" class="auth-wrapper">
      <div class="auth-card">
        <div class="auth-header">
          <div class="brand">
            <div class="brand-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" /></svg>
            </div>
            <h2>Kişi Rehberi</h2>
          </div>
          <p class="subtitle">Kişisel bağlantılarınızı güvenle kaydedin ve yönetin</p>
        </div>

        <div class="auth-tabs">
          <button @click="authTab = 'login'" :class="{ active: authTab === 'login' }">Giriş Yap</button>
          <button @click="authTab = 'register'" :class="{ active: authTab === 'register' }">Kayıt Ol</button>
        </div>

        <!-- Login Form -->
        <form v-if="authTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
          <div class="input-group">
            <label for="login-username">Kullanıcı Adı</label>
            <input v-model="loginForm.username" id="login-username" type="text" placeholder="kullanici_adi" required autocomplete="username">
          </div>
          <div class="input-group">
            <label for="login-password">Şifre</label>
            <input v-model="loginForm.password" id="login-password" type="password" placeholder="••••••••" required autocomplete="current-password">
          </div>
          <button type="submit" class="btn-primary auth-submit">Giriş Yap</button>
        </form>

        <!-- Register Form -->
        <form v-else @submit.prevent="handleRegister" class="auth-form">
          <div class="input-group">
            <label for="reg-username">Kullanıcı Adı</label>
            <input v-model="registerForm.username" id="reg-username" type="text" placeholder="kullanici_adi" required autocomplete="username">
            <span v-if="authErrors.username" class="error-msg">{{ authErrors.username[0] }}</span>
          </div>
          <div class="input-group">
            <label for="reg-email">E-posta Adresi</label>
            <input v-model="registerForm.email" id="reg-email" type="email" placeholder="ornek@eposta.com" required autocomplete="email">
            <span v-if="authErrors.email" class="error-msg">{{ authErrors.email[0] }}</span>
          </div>
          <div class="input-group">
            <label for="reg-password">Şifre (Min. 6 Karakter)</label>
            <input v-model="registerForm.password" id="reg-password" type="password" placeholder="••••••••" required autocomplete="new-password">
            <span v-if="authErrors.password" class="error-msg">{{ authErrors.password[0] }}</span>
          </div>
          <button type="submit" class="btn-primary auth-submit">Hesap Oluştur</button>
        </form>
      </div>
    </div>

    <!-- 2. APPLICATION DASHBOARD (If authenticated) -->
    <div v-else class="dashboard-wrapper">
      <!-- Navbar / Header -->
      <header class="navbar">
        <div class="nav-brand">
          <span class="nav-icon">
            <svg viewBox="0 0 20 20" fill="currentColor" class="w-6 h-6"><path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" /></svg>
          </span>
          <h1>Kişisel Rehberim</h1>
        </div>

        <div class="nav-user-panel" v-if="currentUser">
          <div class="user-avatar" :title="currentUser.email">
            {{ getInitials(currentUser.username) }}
          </div>
          <div class="user-details">
            <span class="username">{{ currentUser.username }}</span>
            <span class="user-email">{{ currentUser.email }}</span>
          </div>
          <button @click="handleLogout" class="btn-logout" title="Çıkış Yap">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" /></svg>
          </button>
        </div>
      </header>

      <!-- Main Section -->
      <main class="container">
        <!-- Search, Filter & Add Button Bar -->
        <section class="action-bar card">
          <div class="search-box">
            <span class="search-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" /></svg>
            </span>
            <input v-model="searchQuery" type="text" placeholder="İsim veya telefon numarası ara...">
          </div>

          <div class="filter-box">
            <select v-model="selectedTag" class="tag-select">
              <option v-for="tag in tags" :key="tag" :value="tag">
                {{ tag === 'Hepsi' ? '🏷️ Tüm Gruplar' : `🏷️ ${tag}` }}
              </option>
            </select>
          </div>

          <button @click="openModal('create')" class="btn-primary btn-add">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
            Yeni Kişi Ekle
          </button>
        </section>

        <!-- Loading state -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>Kişiler yükleniyor...</p>
        </div>

        <!-- Contacts Grid -->
        <div v-else>
          <!-- Empty State -->
          <div v-if="contacts.length === 0" class="empty-state card">
            <div class="empty-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.109A11.956 11.956 0 0112 20.25a11.956 11.956 0 01-3-1.013v-.109m0 0.003c0-1.113.285-2.16.786-3.07M9 19.128v-.003c0-1.113-.285-2.16-.786-3.07M9 19.128A9.38 9.38 0 016.375 19.5a9.337 9.337 0 01-4.121-.952 4.125 4.125 0 017.533-2.493M9 19.128v.109A11.956 11.956 0 0012 20.25a11.956 11.956 0 003-1.013M9 8.25a3 3 0 11-6 0 3 3 0 016 0zm3 0a3 3 0 11-6 0 3 3 0 016 0zm3 0a3 3 0 11-6 0 3 3 0 016 0zm-3 8.25a3.75 3.75 0 100-7.5 3.75 3.75 0 000 7.5z" /></svg>
            </div>
            <h3>Kişi Bulunamadı</h3>
            <p v-if="searchQuery || selectedTag !== 'Hepsi'">Kriterlerinize uygun kişi bulunmamaktadır. Arama metnini değiştirmeyi deneyebilirsiniz.</p>
            <p v-else>Henüz hiç kişi eklemedin, <strong>+ Ekle</strong> butonu ile eklemeye başlayabilirsin.</p>
            <button v-if="!searchQuery && selectedTag === 'Hepsi'" @click="openModal('create')" class="btn-primary" style="margin-top: 15px;">İlk Kişini Ekle</button>
          </div>

          <!-- Contacts Grid Layout -->
          <div v-else class="contacts-grid">
            <div v-for="contact in contacts" :key="contact.id" class="contact-card card" @click="openModal('detail', contact)">
              <div class="card-avatar" :class="`avatar-${contact.tag ? contact.tag.toLowerCase().replace('ı','i').replace('ş','s') : 'diger'}`">
                {{ getInitials(contact.full_name) }}
              </div>
              <div class="card-info">
                <h3 class="contact-name">{{ contact.full_name }}</h3>
                <p class="contact-phone">
                  <svg viewBox="0 0 20 20" fill="currentColor" class="inline-icon"><path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" /></svg>
                  {{ contact.phone }}
                </p>
                <div class="badge-wrapper">
                  <span :class="['badge', `badge-${contact.tag ? contact.tag.toLowerCase().replace('ı','i').replace('ş','s') : 'diger'}`]">{{ contact.tag }}</span>
                </div>
              </div>

              <!-- Inline Action Buttons -->
              <div class="card-actions" @click.stop>
                <button @click="openModal('edit', contact)" class="btn-icon-action btn-edit" title="Düzenle">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487zm0 0L19.5 7.125" /></svg>
                </button>
                <button @click="openModal('delete', contact)" class="btn-icon-action btn-delete" title="Sil">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" /></svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Pagination Controls -->
          <div v-if="totalPages > 1" class="pagination-bar">
            <button @click="fetchContacts(currentPage - 1)" :disabled="currentPage === 1" class="btn-secondary pagination-btn">
              « Önceki
            </button>
            <span class="pagination-info">Sayfa <strong>{{ currentPage }}</strong> / <strong>{{ totalPages }}</strong></span>
            <button @click="fetchContacts(currentPage + 1)" :disabled="currentPage === totalPages" class="btn-secondary pagination-btn">
              Sonraki »
            </button>
          </div>
        </div>
      </main>
    </div>

    <!-- 3. MODALS SYSTEM -->

    <!-- A. Create Contact Modal -->
    <div v-if="activeModal === 'create'" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-header">
          <h3>Yeni Kişi Ekle</h3>
          <button @click="closeModal" class="btn-close-modal">&times;</button>
        </div>
        <form @submit.prevent="handleCreateContact" class="modal-form">
          <div class="input-group">
            <label>Ad Soyad *</label>
            <input v-model="newContact.full_name" type="text" placeholder="Mehmet Yılmaz" required>
          </div>
          <div class="input-group">
            <label>Telefon Numarası *</label>
            <input v-model="newContact.phone" type="tel" placeholder="0555 123 4567" required>
          </div>
          <div class="input-group">
            <label>E-posta Adresi (Opsiyonel)</label>
            <input v-model="newContact.email" type="email" placeholder="mehmet@eposta.com">
          </div>
          <div class="input-group">
            <label>Grup / Etiket</label>
            <select v-model="newContact.tag" class="modal-select">
              <option>Arkadaş</option>
              <option>Aile</option>
              <option>İş</option>
              <option>Diğer</option>
            </select>
          </div>
          <div class="input-group">
            <label>Kısa Not (Opsiyonel)</label>
            <textarea v-model="newContact.note" rows="3" placeholder="Kişi hakkında kısa bir not..."></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-secondary">İptal</button>
            <button type="submit" class="btn-primary">Kaydet</button>
          </div>
        </form>
      </div>
    </div>

    <!-- B. Edit Contact Modal -->
    <div v-if="activeModal === 'edit' && editContactData.id" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-header">
          <h3>Kişiyi Düzenle</h3>
          <button @click="closeModal" class="btn-close-modal">&times;</button>
        </div>
        <form @submit.prevent="handleUpdateContact" class="modal-form">
          <div class="input-group">
            <label>Ad Soyad *</label>
            <input v-model="editContactData.full_name" type="text" required>
          </div>
          <div class="input-group">
            <label>Telefon Numarası *</label>
            <input v-model="editContactData.phone" type="tel" required>
          </div>
          <div class="input-group">
            <label>E-posta Adresi</label>
            <input v-model="editContactData.email" type="email">
          </div>
          <div class="input-group">
            <label>Grup / Etiket</label>
            <select v-model="editContactData.tag" class="modal-select">
              <option>Arkadaş</option>
              <option>Aile</option>
              <option>İş</option>
              <option>Diğer</option>
            </select>
          </div>
          <div class="input-group">
            <label>Kısa Not</label>
            <textarea v-model="editContactData.note" rows="3"></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-secondary">İptal</button>
            <button type="submit" class="btn-primary">Değişiklikleri Kaydet</button>
          </div>
        </form>
      </div>
    </div>

    <!-- C. Detail View Modal -->
    <div v-if="activeModal === 'detail' && selectedContact" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card detail-modal">
        <div class="modal-header">
          <h3>Kişi Detayları</h3>
          <button @click="closeModal" class="btn-close-modal">&times;</button>
        </div>
        <div class="detail-content">
          <div class="detail-profile">
            <div class="detail-avatar" :class="`avatar-${selectedContact.tag ? selectedContact.tag.toLowerCase().replace('ı','i').replace('ş','s') : 'diger'}`">
              {{ getInitials(selectedContact.full_name) }}
            </div>
            <h2>{{ selectedContact.full_name }}</h2>
            <span :class="['badge', `badge-${selectedContact.tag ? selectedContact.tag.toLowerCase().replace('ı','i').replace('ş','s') : 'diger'}`]">{{ selectedContact.tag }}</span>
          </div>

          <div class="detail-fields">
            <div class="detail-field">
              <span class="field-label">
                <svg viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" /></svg>
                Telefon
              </span>
              <span class="field-value">{{ selectedContact.phone }}</span>
            </div>

            <div class="detail-field">
              <span class="field-label">
                <svg viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" /><path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" /></svg>
                E-posta
              </span>
              <span class="field-value">{{ selectedContact.email || '—' }}</span>
            </div>

            <div class="detail-field">
              <span class="field-label">
                <svg viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" /></svg>
                Kısa Not
              </span>
              <span class="field-value note-value">{{ selectedContact.note || 'Henüz bir not eklenmemiş.' }}</span>
            </div>

            <div class="detail-field" v-if="selectedContact.created_at">
              <span class="field-label">
                <svg viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path fill-rule="evenodd" d="M6 2a1 1 0 00-1-1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V4a2 2 0 00-2-2h-1V1a1 1 0 10-2 0v1H7V1a1 1 0 00-1-1zM4 5h12v10H4V5z" clip-rule="evenodd" /></svg>
                Kayıt Tarihi
              </span>
              <span class="field-value">{{ new Date(selectedContact.created_at).toLocaleDateString('tr-TR') }}</span>
            </div>
          </div>

          <div class="modal-actions detail-actions">
            <button @click="openModal('edit', selectedContact)" class="btn-primary">
              Düzenle
            </button>
            <button @click="closeModal" class="btn-secondary">Kapat</button>
          </div>
        </div>
      </div>
    </div>

    <!-- D. Delete Confirm Modal -->
    <div v-if="activeModal === 'delete' && selectedContact" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card confirm-modal">
        <div class="modal-header">
          <h3>Kişiyi Sil</h3>
          <button @click="closeModal" class="btn-close-modal">&times;</button>
        </div>
        <div class="confirm-content">
          <div class="warning-icon">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-12 h-12 text-red-500"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>
          </div>
          <p><strong>{{ selectedContact.full_name }}</strong> kişisini silmek istediğinizden emin misiniz?</p>
          <p class="sub-text">Bu işlem geri alınamaz.</p>
        </div>
        <div class="modal-actions">
          <button @click="closeModal" class="btn-secondary">Vazgeç</button>
          <button @click="handleDeleteContact" class="btn-danger">Evet, Sil</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* CSS VARIABLES & RESET */
:root {
  --primary: hsl(243, 75%, 59%);
  --primary-hover: hsl(243, 75%, 50%);
  --primary-light: hsl(243, 75%, 95%);
  --success: hsl(142, 70%, 45%);
  --success-light: hsl(142, 70%, 95%);
  --danger: #e11d48;
  --danger-hover: #be123c;
  --danger-light: #fff1f2;
  --info: #0284c7;
  --info-light: #f0f9ff;
  --bg-app: #f8fafc;
  --bg-card: #ffffff;
  --border: #e2e8f0;
  --text-main: #334155;
  --text-muted: #64748b;
  --text-heading: #0f172a;
  
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 16px;
}

body {
  background-color: var(--bg-app) !important;
  color: var(--text-main);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  margin: 0;
  padding: 0;
}

/* APP LAYOUT */
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* CARDS */
.card {
  background-color: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  box-shadow: var(--shadow-md);
}

/* BUTTONS */
button {
  font-family: inherit;
  font-weight: 500;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  font-size: 0.95rem;
}

.btn-primary {
  background-color: var(--primary);
  color: white;
  padding: 10px 20px;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: #f1f5f9;
  color: var(--text-main);
  padding: 10px 20px;
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background-color: #e2e8f0;
}

.btn-danger {
  background-color: var(--danger);
  color: white;
  padding: 10px 20px;
}

.btn-danger:hover {
  background-color: var(--danger-hover);
}

/* TOASTS */
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  pointer-events: auto;
  min-width: 280px;
  max-width: 400px;
  animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  border-left: 5px solid transparent;
}

.toast-success {
  background-color: #f0fdf4;
  color: #166534;
  border-left-color: #22c55e;
}

.toast-error {
  background-color: #fef2f2;
  color: #991b1b;
  border-left-color: #ef4444;
}

.toast-info {
  background-color: #f0f9ff;
  color: #075985;
  border-left-color: #0ea5e9;
}

.toast-icon svg {
  width: 20px;
  height: 20px;
}

/* AUTHENTICATION WRAPPER */
.auth-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: radial-gradient(circle at top right, rgba(79, 70, 229, 0.08), transparent 40%),
              radial-gradient(circle at bottom left, rgba(225, 29, 72, 0.03), transparent 30%);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: 40px 30px;
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.brand-icon {
  background-color: var(--primary-light);
  color: var(--primary);
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-icon svg {
  width: 24px;
  height: 24px;
}

.brand h2 {
  font-size: 1.6rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-heading);
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin: 0;
}

.auth-tabs {
  display: flex;
  border-bottom: 2px solid var(--border);
  margin-bottom: 24px;
}

.auth-tabs button {
  flex: 1;
  padding: 12px;
  background: none;
  font-weight: 600;
  color: var(--text-muted);
  border-bottom: 2px solid transparent;
  border-radius: 0;
}

.auth-tabs button:hover {
  color: var(--primary);
}

.auth-tabs button.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-align: left;
}

.input-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-main);
}

.input-group input,
.input-group textarea,
.modal-select {
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  outline: none;
  transition: all 0.2s;
  background-color: #f8fafc;
}

.input-group input:focus,
.input-group textarea:focus,
.modal-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
  background-color: white;
}

.error-msg {
  color: var(--danger);
  font-size: 0.75rem;
  font-weight: 500;
  margin-top: 2px;
}

.auth-submit {
  width: 100%;
  padding: 12px;
  font-weight: 600;
  margin-top: 10px;
}

/* NAVBAR / HEADER */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 40px;
  background-color: white;
  border-bottom: 1px solid var(--border);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-icon {
  background-color: var(--primary-light);
  color: var(--primary);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-brand h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-heading);
  margin: 0;
}

.nav-user-panel {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 38px;
  height: 38px;
  background-color: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.95rem;
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.2;
}

.user-details .username {
  font-weight: 600;
  color: var(--text-heading);
  font-size: 0.9rem;
}

.user-details .user-email {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.btn-logout {
  background: #f1f5f9;
  border: 1px solid var(--border);
  color: var(--text-muted);
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-logout:hover {
  background-color: var(--danger-light);
  color: var(--danger);
  border-color: #fca5a5;
}

.btn-logout svg {
  width: 18px;
  height: 18px;
}

/* MAIN DASHBOARD CONTAINER */
.container {
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
  padding: 30px 20px;
  box-sizing: border-box;
}

/* ACTION BAR */
.action-bar {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 15px;
  padding: 16px 20px;
  align-items: center;
  margin-bottom: 25px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--text-muted);
  pointer-events: none;
}

.search-icon svg {
  width: 18px;
  height: 18px;
}

.search-box input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  outline: none;
  font-size: 0.95rem;
  background-color: #f8fafc;
  transition: all 0.2s;
}

.search-box input:focus {
  border-color: var(--primary);
  background-color: white;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.tag-select {
  padding: 10px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  outline: none;
  background-color: white;
  font-size: 0.95rem;
  color: var(--text-main);
  cursor: pointer;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
}

.btn-add svg {
  width: 18px;
  height: 18px;
}

/* LOADING SPIN */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  gap: 15px;
  color: var(--text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3.5px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* EMPTY STATE */
.empty-state {
  padding: 50px 30px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-icon {
  width: 70px;
  height: 70px;
  background-color: var(--primary-light);
  color: var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.empty-icon svg {
  width: 36px;
  height: 36px;
}

.empty-state h3 {
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--text-heading);
}

.empty-state p {
  color: var(--text-muted);
  font-size: 0.95rem;
  max-width: 400px;
  margin: 0;
}

/* CONTACTS GRID */
.contacts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.contact-card {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  cursor: pointer;
}

.contact-card:hover {
  transform: translateY(-2px);
  border-color: var(--primary);
  box-shadow: var(--shadow-md);
}

.card-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.15rem;
  color: white;
  flex-shrink: 0;
}

.card-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  overflow: hidden;
  text-align: left;
}

.contact-name {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text-heading);
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}

.contact-phone {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0 0 8px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.inline-icon {
  width: 14px;
  height: 14px;
}

.badge-wrapper {
  margin-top: auto;
}

.badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}

/* BADGE & AVATAR TAG COLORS */
.avatar-aile, .badge-aile { background-color: #ec4899; }
.avatar-is, .badge-is { background-color: #4f46e5; }
.avatar-arkadas, .badge-arkadas { background-color: #10b981; }
.avatar-diger, .badge-diger { background-color: #64748b; }

.badge-aile { background-color: #fdf2f8; color: #db2777; border: 1px solid #fbcfe8; }
.badge-is { background-color: #e0e7ff; color: #4f46e5; border: 1px solid #c7d2fe; }
.badge-arkadas { background-color: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }
.badge-diger { background-color: #f8fafc; color: #475569; border: 1px solid #cbd5e1; }

/* CARD ACTIONS */
.card-actions {
  position: absolute;
  right: 15px;
  top: 15px;
  display: flex;
  gap: 5px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.contact-card:hover .card-actions {
  opacity: 1;
}

.btn-icon-action {
  background-color: #f8fafc;
  border: 1px solid var(--border);
  color: var(--text-muted);
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.btn-icon-action svg {
  width: 16px;
  height: 16px;
}

.btn-edit:hover {
  background-color: var(--primary-light);
  color: var(--primary);
  border-color: #c7d2fe;
}

.btn-delete:hover {
  background-color: var(--danger-light);
  color: var(--danger);
  border-color: #fca5a5;
}

/* PAGINATION */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
}

.pagination-btn {
  padding: 8px 16px;
  font-size: 0.85rem;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 0.9rem;
  color: var(--text-muted);
}

/* MODALS SYSTEM */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  box-sizing: border-box;
}

.modal-card {
  width: 100%;
  max-width: 480px;
  background-color: white;
  border-radius: var(--radius-lg);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: modalIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-heading);
  margin: 0;
}

.btn-close-modal {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-muted);
  padding: 0;
  line-height: 1;
}

.btn-close-modal:hover {
  color: var(--text-heading);
}

.modal-form {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.modal-select {
  padding: 10px 14px;
  background-color: #f8fafc;
  border: 1px solid var(--border);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

/* DETAIL MODAL SPECIALS */
.detail-modal {
  max-width: 440px;
}

.detail-content {
  padding: 30px 24px;
}

.detail-profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-bottom: 25px;
}

.detail-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.8rem;
  color: white;
  margin-bottom: 12px;
  box-shadow: var(--shadow-md);
}

.detail-profile h2 {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-heading);
  margin: 0 0 6px;
}

.detail-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 25px;
}

.detail-field {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 8px;
}

.field-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.field-label svg {
  width: 16px;
  height: 16px;
  color: var(--primary);
}

.field-value {
  font-size: 1rem;
  color: var(--text-heading);
  font-weight: 500;
}

.note-value {
  background-color: #f8fafc;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  width: 100%;
  box-sizing: border-box;
  font-style: italic;
  color: var(--text-main);
  border: 1px solid #edf2f7;
  font-size: 0.92rem;
}

.detail-actions {
  justify-content: center;
  gap: 15px;
}

/* CONFIRM MODAL SPECIALS */
.confirm-modal {
  max-width: 400px;
}

.confirm-content {
  padding: 30px 24px;
  text-align: center;
}

.warning-icon {
  color: var(--danger);
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.confirm-content p {
  margin: 0 0 6px;
  font-size: 1.05rem;
  color: var(--text-heading);
}

.confirm-content .sub-text {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin: 0;
}

/* RESPONSIVE MEDIA */
@media (max-width: 600px) {
  .navbar {
    padding: 16px 20px;
  }
  .nav-brand h1 {
    font-size: 1.1rem;
  }
  .user-details {
    display: none;
  }
  .action-bar {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .btn-add {
    width: 100%;
    justify-content: center;
  }
  .contacts-grid {
    grid-template-columns: 1fr;
  }
  .card-actions {
    opacity: 1; /* Show by default on mobile since hover is not possible */
  }
}

/* ANIMATIONS */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>
