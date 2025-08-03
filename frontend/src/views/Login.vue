<template>
  <div class="login-page">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="card shadow-lg border-0 rounded-lg mt-5">
            <div class="card-header">
              <h3 class="text-center font-weight-light my-4">
                <i class="fas fa-hamburger text-danger"></i>
                Big Kahuna Burger HR
              </h3>
              <ul class="nav nav-tabs card-header-tabs" id="authTabs" role="tablist">
                <li class="nav-item" role="presentation">
                  <button 
                    class="nav-link" 
                    :class="{ active: activeTab === 'login' }"
                    @click="activeTab = 'login'"
                  >
                    <i class="fas fa-sign-in-alt"></i> Вход
                  </button>
                </li>
                <li class="nav-item" role="presentation">
                  <button 
                    class="nav-link" 
                    :class="{ active: activeTab === 'register' }"
                    @click="activeTab = 'register'"
                  >
                    <i class="fas fa-user-plus"></i> Регистрация
                  </button>
                </li>
              </ul>
            </div>
            
            <div class="card-body">
              <!-- Error Display -->
              <div v-if="error" class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle"></i>
                {{ error }}
              </div>

              <!-- Login Form -->
              <div v-show="activeTab === 'login'">
                <form @submit.prevent="handleLogin">
                  <div class="form-floating mb-3">
                    <input 
                      type="text" 
                      class="form-control" 
                      id="loginUsername"
                      v-model="loginForm.username"
                      placeholder="Имя пользователя"
                      required
                    >
                    <label for="loginUsername">Имя пользователя</label>
                  </div>
                  
                  <div class="form-floating mb-3">
                    <input 
                      type="password" 
                      class="form-control" 
                      id="loginPassword"
                      v-model="loginForm.password"
                      placeholder="Пароль"
                      required
                    >
                    <label for="loginPassword">Пароль</label>
                  </div>
                  
                  <div class="d-grid">
                    <button 
                      type="submit" 
                      class="btn btn-primary btn-block"
                      :disabled="loading"
                    >
                      <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                      <i class="fas fa-sign-in-alt"></i> Войти
                    </button>
                  </div>
                </form>
              </div>

              <!-- Registration Form -->
              <div v-show="activeTab === 'register'">
                <form @submit.prevent="handleRegister">
                  <div class="form-floating mb-3">
                    <input 
                      type="text" 
                      class="form-control" 
                      id="regUsername"
                      v-model="registerForm.username"
                      placeholder="Имя пользователя"
                      required
                    >
                    <label for="regUsername">Имя пользователя</label>
                  </div>
                  
                  <div class="form-floating mb-3">
                    <input 
                      type="email" 
                      class="form-control" 
                      id="regEmail"
                      v-model="registerForm.email"
                      placeholder="Email"
                      required
                    >
                    <label for="regEmail">Email</label>
                  </div>
                  
                  <div class="form-floating mb-3">
                    <input 
                      type="text" 
                      class="form-control" 
                      id="regFullName"
                      v-model="registerForm.full_name"
                      placeholder="Полное имя"
                    >
                    <label for="regFullName">Полное имя</label>
                  </div>
                  
                  <div class="form-floating mb-3">
                    <textarea 
                      class="form-control" 
                      id="regNotes"
                      v-model="registerForm.personal_notes"
                      placeholder="Личные заметки"
                      style="height: 100px"
                    ></textarea>
                    <label for="regNotes">Личные заметки (необязательно)</label>
                    <div class="form-text text-muted">
                      <small>Расскажите немного о себе и ваших карьерных интересах</small>
                    </div>
                  </div>
                  
                  <div class="form-floating mb-3">
                    <input 
                      type="password" 
                      class="form-control" 
                      id="regPassword"
                      v-model="registerForm.password"
                      placeholder="Пароль"
                      required
                    >
                    <label for="regPassword">Пароль</label>
                  </div>
                  
                  <div class="d-grid">
                    <button 
                      type="submit" 
                      class="btn btn-success btn-block"
                      :disabled="loading"
                    >
                      <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                      <i class="fas fa-user-plus"></i> Зарегистрироваться
                    </button>
                  </div>
                </form>
              </div>
            </div>
            
            <div class="card-footer text-center py-3">
              <div class="small">
                <strong>Обучающая платформа:</strong> Содержит преднамеренные уязвимости
              </div>
            </div>
          </div>


        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      activeTab: 'login',
      loginForm: {
        username: '',
        password: ''
      },
      registerForm: {
        username: '',
        email: '',
        full_name: '',
        personal_notes: '', // Vulnerable to XSS
        password: ''
      }
    }
  },
  computed: {
    ...mapGetters(['loading', 'error'])
  },
  methods: {
    ...mapActions(['login', 'register']),
    
    async handleLogin() {
      try {
        await this.login(this.loginForm)
        this.$router.push(this.isHR ? '/hr/dashboard' : '/candidate-portal')
      } catch (error) {
        // Error is handled by the store
      }
    },
    
    async handleRegister() {
      try {
        await this.register(this.registerForm)
        this.activeTab = 'login'
        this.loginForm.username = this.registerForm.username
        alert('Регистрация прошла успешно! Пожалуйста, войдите с вашими учетными данными.')
      } catch (error) {
        // Error is handled by the store
      }
    }
  },
  
  // Check if already logged in
  beforeMount() {
    if (this.$store.getters.isAuthenticated) {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.login-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: calc(100vh - 120px);
  padding: 50px 0;
}

.card {
  border: none;
  border-radius: 1rem;
}

.card-header {
  border-bottom: none;
  background: transparent;
}

.nav-tabs .nav-link {
  border: none;
  color: #6c757d;
}

.nav-tabs .nav-link.active {
  background-color: transparent;
  border-bottom: 2px solid #dc3545;
  color: #dc3545;
  font-weight: bold;
}

.form-floating > .form-control:focus ~ label {
  color: #dc3545;
}

.form-floating > .form-control:focus {
  border-color: #dc3545;
  box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25);
}

.text-monospace {
  font-family: 'Courier New', monospace;
  background-color: #f8f9fa;
  padding: 0.25rem;
  border-radius: 0.25rem;
}


</style> 