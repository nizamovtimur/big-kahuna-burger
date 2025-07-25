<template>
  <div class="login-page">
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
          <div class="card shadow">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <i class="fas fa-user-shield fa-3x text-primary mb-3"></i>
                <h3 class="fw-bold">HR Portal Login</h3>
                <p class="text-muted">Access your HR dashboard</p>
              </div>

              <!-- Login Form -->
              <form @submit.prevent="handleLogin" v-if="!showRegister">
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input 
                    v-model="loginForm.email" 
                    type="email" 
                    class="form-control" 
                    placeholder="Enter your email"
                    required
                  >
                </div>
                
                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input 
                    v-model="loginForm.password" 
                    type="password" 
                    class="form-control" 
                    placeholder="Enter your password"
                    required
                  >
                </div>
                
                <button 
                  type="submit" 
                  class="btn btn-primary w-100 mb-3"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Sign In
                </button>
                
                <div class="text-center">
                  <button 
                    type="button" 
                    class="btn btn-link" 
                    @click="showRegister = true"
                  >
                    Need an account? Register here
                  </button>
                </div>
              </form>

              <!-- Register Form -->
              <form @submit.prevent="handleRegister" v-if="showRegister">
                <div class="mb-3">
                  <label class="form-label">Full Name</label>
                  <input 
                    v-model="registerForm.full_name" 
                    type="text" 
                    class="form-control" 
                    required
                  >
                </div>
                
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input 
                    v-model="registerForm.email" 
                    type="email" 
                    class="form-control" 
                    required
                  >
                </div>
                
                <div class="mb-3">
                  <label class="form-label">Department</label>
                  <select v-model="registerForm.department" class="form-select">
                    <option value="Human Resources">Human Resources</option>
                    <option value="Operations">Operations</option>
                    <option value="Management">Management</option>
                  </select>
                </div>
                
                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input 
                    v-model="registerForm.password" 
                    type="password" 
                    class="form-control" 
                    required
                  >
                </div>
                
                <button 
                  type="submit" 
                  class="btn btn-success w-100 mb-3"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Register
                </button>
                
                <div class="text-center">
                  <button 
                    type="button" 
                    class="btn btn-link" 
                    @click="showRegister = false"
                  >
                    Already have an account? Sign in
                  </button>
                </div>
              </form>

              <!-- Error Message -->
              <div v-if="error" class="alert alert-danger mt-3">
                {{ error }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      showRegister: false,
      loginForm: {
        email: '',
        password: ''
      },
      registerForm: {
        email: '',
        password: '',
        full_name: '',
        department: 'Human Resources'
      }
    }
  },
  computed: {
    ...mapState(['loading', 'error'])
  },
  methods: {
    ...mapActions(['login', 'register']),
    
    async handleLogin() {
      const result = await this.login(this.loginForm)
      if (result.success) {
        this.$router.push('/hr/dashboard')
      }
    },
    
    async handleRegister() {
      const result = await this.register(this.registerForm)
      if (result.success) {
        this.$router.push('/hr/dashboard')
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: calc(100vh - 76px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
}

.card {
  border: none;
  border-radius: 15px;
}
</style> 