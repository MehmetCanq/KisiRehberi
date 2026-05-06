<script setup>
import {ref, onMounted} from "vue";
import api from './api.js'

const contacts = ref([]);
const loading = ref(true);
const isAuthenticated = ref(false);

// Login form
const loginForm = ref({
  username: '',
  password: ''
});

const newContact = ref({
  full_name:'',
  phone:'',
  tag:'Diğer'
});

const login = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    alert("Lütfen kullanıcı adı ve şifre girin");
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
    loginForm.value = { username: '', password: '' };
    fetchContacts();
  } catch (error) {
    alert("Giriş başarısız: " + (error.response?.data?.detail || "Bilinmeyen hata"));
  }
};

const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  isAuthenticated.value = false;
  contacts.value = [];
};

const fetchContacts = async () => {
  try {
    const response = await api.get('contacts/');
    contacts.value = response.data.results || response.data;
  } catch (error) {
    console.error('Veriler çekilemedi:', error);
  } finally {
    loading.value = false;
  }
};

const saveContact = async () => {
  if (!newContact.value.full_name || !newContact.value.phone) {
    alert("Lütfen isim ve telefon bölümlerini doldurun");
    return;
  }
  try {
    await api.post('contacts/',newContact.value);
    newContact.value = {full_name: '',phone:'',tag:'Diğer'};
    fetchContacts();
  }
  catch (error) {
    console.error("Kaydedilirken hata oluştu",error);
    alert("Kaydedilirken hata oluştu: " + (error.response?.data?.detail || error.message));
  }
};

onMounted(() => {
  const token = localStorage.getItem('access_token');
  if (token) {
    isAuthenticated.value = true;
    fetchContacts();
  }
});
</script>

<template>
  <div class="container">
    <h1> KİŞİSEL REHBERİM</h1>

    <!-- Login Form -->
    <div v-if="!isAuthenticated" class="card">
      <h3>Giriş Yapın</h3>
      <div class="form-group">
        <input v-model="loginForm.username" placeholder="Kullanıcı Adı" type="text">
        <input v-model="loginForm.password" placeholder="Şifre" type="password">
        <button @click="login">Giriş Yap</button>
      </div>
    </div>

    <!-- Contact Form -->
    <div v-else>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h3>Yeni kişi ekle</h3>
        <button @click="logout" style="background: #dc3545; padding: 5px 10px; margin: 0;">Çıkış Yap</button>
      </div>

      <div class="card">
        <div class="form-group">
          <input v-model="newContact.full_name" placeholder="Ad Soyad">
          <input v-model="newContact.phone" placeholder="Telefon no">
          <select v-model="newContact.tag">
            <option>İş</option>
            <option>Aile</option>
            <option>Arkadaş</option>
            <option>Diğer</option>
          </select>
          <button @click="saveContact">Kaydet</button>
        </div>
      </div>

    <hr>

    <div v-if="loading">Yükleniyor...</div>
    <ul v-else class="contact-list">
      <template v-for="contact in contacts" :key="contact ? contact.id : Math.random()" class="contact-item">
        <li v-if="contact" class="contact-item">
          <div>
            <strong>{{ contact.full_name }}</strong> <br>
            <small>{{ contact.phone }}</small>
          </div>
          <span class="badge">{{ contact.tag }}</span>
        </li>
      </template>
    </ul>
    </div>
  </div>
</template>

<style scoped>
.container {max-width:600px; margin:0 auto; padding:20px; font-family: sans-serif;}
.card { background:#f9f9f9; padding:20px; border-radius:8px; margin-bottom:20px; border:1px solid #ddd;}
.form-group { display:flex; flex-direction: column; gap:10px;}
input, select { padding:10px; border:1px solid #ccc; border-radius:4px;}
button { padding:10px; background:#007BFF; color:#fff; cursor:pointer; font-weight:bold; border:none; border-radius:4px;}
button:hover { background:#0056b3;}
.contact-list{ list-style:none; padding:0;}
.contact-item { display:flex; justify-content:space-between; align-items:center; padding:10px; border-bottom:1px solid #eee;}
.badge { background:#3498db; color:#fff; padding:3px 8px; border-radius:10px; font-size:12px;}
</style>
